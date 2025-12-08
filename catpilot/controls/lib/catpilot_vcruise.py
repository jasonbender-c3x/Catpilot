#!/usr/bin/env python3
from catpilot.common.conversions import Conversions as CV
from catpilot.common.realtime import DT_MDL
from catpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import COMFORT_BRAKE

from catpilot.catpilot.common.catpilot_variables import CRUISING_SPEED, PLANNER_TIME
from catpilot.catpilot.controls.lib.map_turn_speed_controller import MapTurnSpeedController
from catpilot.catpilot.controls.lib.speed_limit_controller import SpeedLimitController

TARGET_LAT_A = 2.0

class CatPilotVCruise:
  def __init__(self, CatPilotPlanner):
    self.catpilot_planner = CatPilotPlanner

    self.mtsc = MapTurnSpeedController()
    self.slc = SpeedLimitController()

    self.forcing_stop = False
    self.override_force_stop = False

    self.mtsc_target = 0
    self.override_force_stop_timer = 0

  def update(self, gps_position, v_cruise, v_ego, sm, catpilot_toggles):
    force_stop = self.catpilot_planner.cem.stop_light_detected and sm["controlsState"].enabled and catpilot_toggles.force_stops
    force_stop &= self.catpilot_planner.model_stopped
    force_stop &= self.override_force_stop_timer <= 0

    self.force_stop_timer = self.force_stop_timer + DT_MDL if force_stop else 0

    force_stop_enabled = self.force_stop_timer >= 1

    self.override_force_stop |= sm["carState"].gasPressed
    self.override_force_stop |= sm["catpilotCarState"].accelPressed
    self.override_force_stop &= force_stop_enabled

    if self.override_force_stop:
      self.override_force_stop_timer = 10
    elif self.override_force_stop_timer > 0:
      self.override_force_stop_timer -= DT_MDL

    v_cruise_cluster = max(sm["controlsState"].vCruiseCluster * CV.KPH_TO_MS, v_cruise)
    v_cruise_diff = v_cruise_cluster - v_cruise

    v_ego_cluster = max(sm["carState"].vEgoCluster, v_ego)
    v_ego_diff = v_ego_cluster - v_ego

    # Mike's extended lead linear braking
    if self.catpilot_planner.lead_one.vLead < v_ego > CRUISING_SPEED and sm["controlsState"].enabled and self.catpilot_planner.tracking_lead and catpilot_toggles.human_following:
      if not self.catpilot_planner.catpilot_following.following_lead:
        decel_rate = (v_ego - self.catpilot_planner.lead_one.vLead)**2 / self.catpilot_planner.lead_one.dRel
        self.braking_target = max(v_ego - (decel_rate * DT_MDL), self.catpilot_planner.lead_one.vLead + CRUISING_SPEED)
      else:
        self.braking_target = v_cruise
    else:
      self.braking_target = v_cruise

    # Pfeiferj's Map Turn Speed Controller
    if v_ego > CRUISING_SPEED and sm["controlsState"].enabled and catpilot_toggles.map_turn_speed_controller:
      mtsc_active = self.mtsc_target < v_cruise

      if self.catpilot_planner.road_curvature_detected and mtsc_active:
        self.mtsc_target = self.mtsc_target
      elif not self.catpilot_planner.road_curvature_detected and catpilot_toggles.mtsc_curvature_check:
        self.mtsc_target = v_cruise
      else:
        mtsc_speed = ((TARGET_LAT_A * catpilot_toggles.turn_aggressiveness) / (self.mtsc.get_map_curvature(gps_position, v_ego) * catpilot_toggles.curve_sensitivity))**0.5
        self.mtsc_target = max(CRUISING_SPEED, mtsc_speed)
    else:
      self.mtsc_target = v_cruise

    # Pfeiferj's Speed Limit Controller
    self.slc.catpilot_toggles = catpilot_toggles

    if catpilot_toggles.speed_limit_controller:
      self.slc.update_limits(sm["catpilotCarState"].dashboardSpeedLimit, gps_position, sm["catpilotNavigation"].navigationSpeedLimit, v_cruise, v_ego, sm)
      self.slc.update_override(v_cruise, v_cruise_diff, v_ego, v_ego_diff, sm)

      self.slc_offset = self.slc.offset
      self.slc_target = self.slc.target
    elif catpilot_toggles.show_speed_limits:
      self.slc.update_limits(sm["catpilotCarState"].dashboardSpeedLimit, gps_position, sm["catpilotNavigation"].navigationSpeedLimit, v_cruise, v_ego, sm)

      self.slc_offset = 0
      self.slc_target = self.slc.target
    else:
      self.slc_offset = 0
      self.slc_target = 0

    # Pfeiferj's Vision Turn Controller
    if v_ego > CRUISING_SPEED and sm["controlsState"].enabled and self.catpilot_planner.road_curvature_detected and catpilot_toggles.vision_turn_speed_controller:
      vtsc_speed = ((TARGET_LAT_A * catpilot_toggles.turn_aggressiveness) / (abs(self.catpilot_planner.road_curvature) * catpilot_toggles.curve_sensitivity))**0.5
      self.vtsc_target = max(CRUISING_SPEED, vtsc_speed)
    else:
      self.vtsc_target = v_cruise

    if sm["carState"].standstill and not self.override_force_stop and sm["controlsState"].enabled and catpilot_toggles.force_standstill:
      self.forcing_stop = True

      v_cruise = -1

    elif force_stop_enabled and not self.override_force_stop:
      self.forcing_stop |= not sm["carState"].standstill

      self.tracked_model_length = max(self.tracked_model_length - (v_ego * DT_MDL), 0)
      v_cruise = min((self.tracked_model_length // PLANNER_TIME), v_cruise)

    else:
      self.forcing_stop = False

      self.tracked_model_length = self.catpilot_planner.model_length

      targets = [self.braking_target, self.mtsc_target, self.vtsc_target, v_cruise]
      if catpilot_toggles.speed_limit_controller:
        targets.append(max(self.slc.overridden_speed, self.slc_target + self.slc_offset) - v_ego_diff)

      v_cruise = min([target if target > CRUISING_SPEED else v_cruise for target in targets])

    self.mtsc_target += v_cruise_diff
    self.vtsc_target += v_cruise_diff

    return v_cruise
