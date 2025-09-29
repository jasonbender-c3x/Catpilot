#!/usr/bin/env python3
import json
import math

import cereal.messaging as messaging

from cereal import car, log
from openpilot.common.conversions import Conversions as CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL

from openpilot.selfdrive.controls.lib.drive_helpers import V_CRUISE_MAX
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import A_CHANGE_COST, DANGER_ZONE_COST, J_EGO_COST, STOP_DISTANCE

from openpilot.catpilot.common.catpilot_utilities import calculate_lane_width, calculate_road_curvature
from openpilot.catpilot.common.catpilot_variables import CRUISING_SPEED, MINIMUM_LATERAL_ACCELERATION, PLANNER_TIME, THRESHOLD, params, params_memory
from openpilot.catpilot.controls.lib.conditional_experimental_mode import ConditionalExperimentalMode
from openpilot.catpilot.controls.lib.catpilot_acceleration import CatPilotAcceleration
from openpilot.catpilot.controls.lib.catpilot_events import CatPilotEvents
from openpilot.catpilot.controls.lib.catpilot_following import CatPilotFollowing
from openpilot.catpilot.controls.lib.catpilot_vcruise import CatPilotVCruise

class CatPilotPlanner:
  def __init__(self):
    self.cem = ConditionalExperimentalMode(self)
    self.catpilot_acceleration = CatPilotAcceleration(self)
    self.catpilot_events = CatPilotEvents(self)
    self.catpilot_following = CatPilotFollowing(self)
    self.catpilot_vcruise = CatPilotVCruise(self)

    with car.CarParams.from_bytes(params.get("CarParams", block=True)) as msg:
      self.CP = msg

    self.tracking_lead_filter = FirstOrderFilter(0, 1, DT_MDL)

    self.driving_in_curve = False
    self.lateral_check = False
    self.model_stopped = False
    self.road_curvature_detected = False
    self.slower_lead = False
    self.tracking_lead = False

    self.lane_width_left = 0
    self.lane_width_right = 0
    self.lateral_acceleration = 0
    self.model_length = 0
    self.road_curvature = 0
    self.v_cruise = 0

  def update(self, sm, catpilot_toggles):
    self.lead_one = sm["radarState"].leadOne

    v_cruise = min(sm["controlsState"].vCruise, V_CRUISE_MAX) * CV.KPH_TO_MS
    v_ego = max(sm["carState"].vEgo, 0)

    if sm["controlsState"].enabled:
      self.catpilot_acceleration.update(v_ego, sm, catpilot_toggles)
    else:
      self.catpilot_acceleration.max_accel = 0
      self.catpilot_acceleration.min_accel = 0

    if sm["controlsState"].enabled and catpilot_toggles.conditional_experimental_mode:
      self.cem.update(v_ego, sm, catpilot_toggles)
    else:
      self.cem.curve_detected = False
      self.cem.stop_sign_and_light(v_ego, sm, PLANNER_TIME - 2)

    self.driving_in_curve = abs(self.lateral_acceleration) >= MINIMUM_LATERAL_ACCELERATION

    self.catpilot_events.update(v_cruise, sm, catpilot_toggles)

    self.catpilot_following.update(v_ego, sm, catpilot_toggles)

    localizer_valid = (sm["liveLocationKalman"].status == log.LiveLocationKalman.Status.valid) and sm["liveLocationKalman"].positionGeodetic.valid
    if sm["liveLocationKalman"].gpsOK and localizer_valid:
      gps_position = {
        "latitude": sm["liveLocationKalman"].positionGeodetic.value[0],
        "longitude": sm["liveLocationKalman"].positionGeodetic.value[1],
        "bearing": math.degrees(sm["liveLocationKalman"].calibratedOrientationNED.value[2])
      }

      params_memory.put("LastGPSPosition", json.dumps(gps_position))
    else:
      gps_position = None

      params_memory.remove("LastGPSPosition")

    self.lateral_acceleration = v_ego**2 * (sm["carState"].steeringAngleDeg - sm["liveParameters"].angleOffsetDeg) * CV.DEG_TO_RAD / (self.CP.steerRatio * self.CP.wheelbase)

    check_lane_width = catpilot_toggles.adjacent_paths or catpilot_toggles.adjacent_path_metrics or catpilot_toggles.blind_spot_path or catpilot_toggles.lane_detection
    if check_lane_width and v_ego >= catpilot_toggles.minimum_lane_change_speed:
      self.lane_width_left = calculate_lane_width(sm["modelV2"].laneLines[0], sm["modelV2"].laneLines[1], sm["modelV2"].roadEdges[0])
      self.lane_width_right = calculate_lane_width(sm["modelV2"].laneLines[3], sm["modelV2"].laneLines[2], sm["modelV2"].roadEdges[1])
    else:
      self.lane_width_left = 0
      self.lane_width_right = 0

    self.lateral_check = v_ego >= catpilot_toggles.pause_lateral_below_speed
    self.lateral_check |= not (sm["carState"].leftBlinker or sm["carState"].rightBlinker) and catpilot_toggles.pause_lateral_below_signal
    self.lateral_check |= sm["carState"].standstill

    self.model_length = sm["modelV2"].position.x[-1]

    self.model_stopped = self.model_length < CRUISING_SPEED * PLANNER_TIME
    self.model_stopped |= self.catpilot_vcruise.forcing_stop

    self.road_curvature = calculate_road_curvature(sm["modelV2"], v_ego)

    self.road_curvature_detected = (1 / abs(self.road_curvature))**0.5 < v_ego > CRUISING_SPEED and not (sm["carState"].leftBlinker or sm["carState"].rightBlinker)

    if not sm["carState"].standstill:
      self.tracking_lead = self.update_lead_status()

    self.v_cruise = self.catpilot_vcruise.update(gps_position, v_cruise, v_ego, sm, catpilot_toggles)

  def update_lead_status(self):
    following_lead = self.lead_one.status
    following_lead &= self.lead_one.dRel < self.model_length + STOP_DISTANCE

    self.tracking_lead_filter.update(following_lead)
    return self.tracking_lead_filter.x >= THRESHOLD**2

  def publish(self, sm, pm, theme_updated, toggles_updated):
    catpilot_plan_send = messaging.new_message("catpilotPlan")
    catpilot_plan_send.valid = sm.all_checks(service_list=["carState", "controlsState"])
    catpilotPlan = catpilot_plan_send.catpilotPlan

    catpilotPlan.accelerationJerk = A_CHANGE_COST * self.catpilot_following.acceleration_jerk
    catpilotPlan.accelerationJerkStock = A_CHANGE_COST * self.catpilot_following.base_acceleration_jerk
    catpilotPlan.dangerJerk = DANGER_ZONE_COST * self.catpilot_following.danger_jerk
    catpilotPlan.speedJerk = J_EGO_COST * self.catpilot_following.speed_jerk
    catpilotPlan.speedJerkStock = J_EGO_COST * self.catpilot_following.base_speed_jerk
    catpilotPlan.tFollow = self.catpilot_following.t_follow

    catpilotPlan.desiredFollowDistance = self.catpilot_following.desired_follow_distance

    catpilotPlan.experimentalMode = self.cem.experimental_mode or self.catpilot_vcruise.slc.experimental_mode

    catpilotPlan.forcingStop = self.catpilot_vcruise.forcing_stop
    catpilotPlan.forcingStopLength = self.catpilot_vcruise.tracked_model_length

    catpilotPlan.catpilotEvents = self.catpilot_events.events.to_msg()

    catpilotPlan.laneWidthLeft = self.lane_width_left
    catpilotPlan.laneWidthRight = self.lane_width_right

    catpilotPlan.lateralCheck = self.lateral_check

    catpilotPlan.maxAcceleration = self.catpilot_acceleration.max_accel
    catpilotPlan.minAcceleration = self.catpilot_acceleration.min_accel

    catpilotPlan.mtscSpeed = self.catpilot_vcruise.mtsc_target
    catpilotPlan.vtscControllingCurve = self.catpilot_vcruise.mtsc_target > self.catpilot_vcruise.vtsc_target
    catpilotPlan.vtscSpeed = self.catpilot_vcruise.vtsc_target

    catpilotPlan.redLight = self.cem.stop_light_detected

    catpilotPlan.roadCurvature = self.road_curvature

    catpilotPlan.slcMapSpeedLimit = self.catpilot_vcruise.slc.map_speed_limit
    catpilotPlan.slcMapboxSpeedLimit = self.catpilot_vcruise.slc.mapbox_limit
    catpilotPlan.slcNextSpeedLimit = self.catpilot_vcruise.slc.next_speed_limit
    catpilotPlan.slcOverriddenSpeed = self.catpilot_vcruise.slc.overridden_speed
    catpilotPlan.slcSpeedLimit = self.catpilot_vcruise.slc_target
    catpilotPlan.slcSpeedLimitOffset = self.catpilot_vcruise.slc_offset
    catpilotPlan.slcSpeedLimitSource = self.catpilot_vcruise.slc.source
    catpilotPlan.speedLimitChanged = self.catpilot_vcruise.slc.speed_limit_changed_timer > DT_MDL
    catpilotPlan.unconfirmedSlcSpeedLimit = self.catpilot_vcruise.slc.unconfirmed_speed_limit

    catpilotPlan.themeUpdated = theme_updated

    catpilotPlan.togglesUpdated = toggles_updated

    catpilotPlan.trackingLead = self.tracking_lead

    catpilotPlan.vCruise = self.v_cruise

    pm.send("catpilotPlan", catpilot_plan_send)
