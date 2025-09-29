#!/usr/bin/env python3
import json

from openpilot.common.realtime import DT_MDL

from openpilot.catpilot.common.catpilot_variables import params, params_tracking

class CatPilotTracking:
  def __init__(self):
    self.catpilot_stats = json.loads(params.get("CatPilotStats") or "{}")

    self.total_drives = params_tracking.get_int("CatPilotDrives")
    self.total_kilometers = params_tracking.get_float("CatPilotKilometers")
    self.total_minutes = params_tracking.get_float("CatPilotMinutes")

    self.drive_added = False
    self.enabled = False

    self.aol_engaged_time = 0
    self.drive_distance = 0
    self.drive_time = 0
    self.lateral_engaged_time = 0
    self.longitudinal_engaged_time = 0

    self.total_aol_engaged = self.catpilot_stats.get("TotalAOLTime", 0)
    self.total_lateral_engaged = self.catpilot_stats.get("TotalLateralTime", 0)
    self.total_longitudinal_engaged = self.catpilot_stats.get("TotalLongitudinalTime", 0)
    self.total_tracked_time = self.catpilot_stats.get("TotalTrackedTime", 0)

  def update(self, sm):
    self.enabled |= sm["controlsState"].enabled or sm["catpilotCarState"].alwaysOnLateralEnabled

    self.drive_distance += sm["carState"].vEgo * DT_MDL
    self.drive_time += DT_MDL

    if sm["carControl"].latActive:
      self.lateral_engaged_time += DT_MDL
    if sm["carControl"].longActive:
      self.longitudinal_engaged_time += DT_MDL
    elif sm["catpilotCarState"].alwaysOnLateralEnabled:
      self.aol_engaged_time += DT_MDL

    if self.drive_time > 60 and sm["carState"].standstill and self.enabled:
      self.total_kilometers += self.drive_distance / 1000
      params_tracking.put_float_nonblocking("CatPilotKilometers", self.total_kilometers)
      self.drive_distance = 0

      self.total_minutes += self.drive_time / 60
      params_tracking.put_float_nonblocking("CatPilotMinutes", self.total_minutes)

      self.total_aol_engaged += self.aol_engaged_time
      self.total_lateral_engaged += self.lateral_engaged_time
      self.total_longitudinal_engaged += self.longitudinal_engaged_time
      self.total_tracked_time += self.drive_time

      self.catpilot_stats["TotalAOLTime"] = self.total_aol_engaged
      self.catpilot_stats["TotalLateralTime"] = self.total_lateral_engaged
      self.catpilot_stats["TotalLongitudinalTime"] = self.total_longitudinal_engaged
      self.catpilot_stats["TotalTrackedTime"] = self.total_tracked_time

      params.put("CatPilotStats", json.dumps(self.catpilot_stats))

      self.aol_engaged_time = 0
      self.drive_time = 0
      self.lateral_engaged_time = 0
      self.longitudinal_engaged_time = 0

      if not self.drive_added:
        self.total_drives += 1
        params_tracking.put_int_nonblocking("CatPilotDrives", self.total_drives)
        self.drive_added = True
