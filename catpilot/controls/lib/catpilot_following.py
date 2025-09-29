#!/usr/bin/env python3
import numpy as np

from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import COMFORT_BRAKE, STOP_DISTANCE, desired_follow_distance, get_jerk_factor, get_T_FOLLOW

from openpilot.catpilot.common.catpilot_variables import CITY_SPEED_LIMIT

TRAFFIC_MODE_BP = [0., CITY_SPEED_LIMIT]

class CatPilotFollowing:
  def __init__(self, CatPilotPlanner):
    self.catpilot_planner = CatPilotPlanner

    self.following_lead = False
    self.slower_lead = False

    self.acceleration_jerk = 0
    self.danger_jerk = 0
    self.desired_follow_distance = 0
    self.speed_jerk = 0
    self.t_follow = 0

  def update(self, v_ego, sm, catpilot_toggles):
    if sm["controlsState"].enabled and sm["catpilotCarState"].trafficModeEnabled:
      if sm["carState"].aEgo >= 0:
        self.base_acceleration_jerk = float(np.interp(v_ego, TRAFFIC_MODE_BP, catpilot_toggles.traffic_mode_jerk_acceleration))
        self.base_speed_jerk = float(np.interp(v_ego, TRAFFIC_MODE_BP, catpilot_toggles.traffic_mode_jerk_speed))
      else:
        self.base_acceleration_jerk = float(np.interp(v_ego, TRAFFIC_MODE_BP, catpilot_toggles.traffic_mode_jerk_deceleration))
        self.base_speed_jerk = float(np.interp(v_ego, TRAFFIC_MODE_BP, catpilot_toggles.traffic_mode_jerk_speed_decrease))

      self.base_danger_jerk = float(np.interp(v_ego, TRAFFIC_MODE_BP, catpilot_toggles.traffic_mode_jerk_danger))
      self.t_follow = float(np.interp(v_ego, TRAFFIC_MODE_BP, catpilot_toggles.traffic_mode_follow))
    elif sm["controlsState"].enabled:
      if sm["carState"].aEgo >= 0:
        self.base_acceleration_jerk, self.base_danger_jerk, self.base_speed_jerk = get_jerk_factor(
          catpilot_toggles.aggressive_jerk_acceleration, catpilot_toggles.aggressive_jerk_danger, catpilot_toggles.aggressive_jerk_speed,
          catpilot_toggles.standard_jerk_acceleration, catpilot_toggles.standard_jerk_danger, catpilot_toggles.standard_jerk_speed,
          catpilot_toggles.relaxed_jerk_acceleration, catpilot_toggles.relaxed_jerk_danger, catpilot_toggles.relaxed_jerk_speed,
          catpilot_toggles.custom_personalities, sm["controlsState"].personality
        )
      else:
        self.base_acceleration_jerk, self.base_danger_jerk, self.base_speed_jerk = get_jerk_factor(
          catpilot_toggles.aggressive_jerk_deceleration, catpilot_toggles.aggressive_jerk_danger, catpilot_toggles.aggressive_jerk_speed_decrease,
          catpilot_toggles.standard_jerk_deceleration, catpilot_toggles.standard_jerk_danger, catpilot_toggles.standard_jerk_speed_decrease,
          catpilot_toggles.relaxed_jerk_deceleration, catpilot_toggles.relaxed_jerk_danger, catpilot_toggles.relaxed_jerk_speed_decrease,
          catpilot_toggles.custom_personalities, sm["controlsState"].personality
        )

      self.t_follow = get_T_FOLLOW(
        catpilot_toggles.aggressive_follow,
        catpilot_toggles.standard_follow,
        catpilot_toggles.relaxed_follow,
        catpilot_toggles.custom_personalities, sm["controlsState"].personality
      )
    else:
      self.base_acceleration_jerk = 0
      self.base_danger_jerk = 0
      self.base_speed_jerk = 0
      self.t_follow = 0

    self.acceleration_jerk = self.base_acceleration_jerk
    self.danger_jerk = self.base_danger_jerk
    self.speed_jerk = self.base_speed_jerk

    self.following_lead = self.catpilot_planner.tracking_lead and self.catpilot_planner.lead_one.dRel < (self.t_follow + 1) * v_ego

    if sm["controlsState"].enabled and self.catpilot_planner.tracking_lead:
      self.update_follow_values(self.catpilot_planner.lead_one.dRel, v_ego, self.catpilot_planner.lead_one.vLead, catpilot_toggles)
      self.desired_follow_distance = int(desired_follow_distance(v_ego, self.catpilot_planner.lead_one.vLead, self.t_follow))
    else:
      self.desired_follow_distance = 0

  def update_follow_values(self, lead_distance, v_ego, v_lead, catpilot_toggles):
    # Offset by CatAi for CatPilot for a more natural approach to a faster lead
    if catpilot_toggles.human_following and v_lead > v_ego:
      distance_factor = max(lead_distance - (v_ego * self.t_follow), 1)
      accelerating_offset = float(np.clip(STOP_DISTANCE - v_ego, 1, distance_factor))

      self.acceleration_jerk /= accelerating_offset
      self.speed_jerk /= accelerating_offset
      self.t_follow /= accelerating_offset

    # Offset by CatAi for CatPilot for a more natural approach to a slower lead
    if (catpilot_toggles.conditional_slower_lead or catpilot_toggles.human_following) and v_lead < v_ego:
      distance_factor = max(lead_distance - (v_lead * self.t_follow), 1)
      braking_offset = float(np.clip(min(v_ego - v_lead, v_lead) - COMFORT_BRAKE, 1, distance_factor))

      if catpilot_toggles.human_following:
        if not self.following_lead and v_lead > CITY_SPEED_LIMIT:
          far_lead_offset = max(lead_distance - (v_ego * self.t_follow) - STOP_DISTANCE, 0)
        else:
          far_lead_offset = 0
        self.t_follow /= braking_offset + far_lead_offset
      self.slower_lead = braking_offset > 1
