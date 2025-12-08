#!/usr/bin/env python3

import time
from multiprocessing import Process

from catpilot.common.params import Params
from catpilot.system.manager.process import launcher
from catpilot.common.swaglog import cloudlog
from catpilot.system.hardware import HARDWARE
from catpilot.system.version import get_build_metadata

ATHENA_MGR_PID_PARAM = "AthenadPid"


def main():
  params = Params()
  dongle_id = params.get("DongleId").decode('utf-8')
  build_metadata = get_build_metadata()

  cloudlog.bind_global(dongle_id=dongle_id,
                       version=build_metadata.catpilot.version,
                       origin=build_metadata.catpilot.git_normalized_origin,
                       branch=build_metadata.channel,
                       commit=build_metadata.catpilot.git_commit,
                       dirty=build_metadata.catpilot.is_dirty,
                       device=HARDWARE.get_device_type())

  try:
    while 1:
      cloudlog.info("starting athena daemon")
      proc = Process(name='athenad', target=launcher, args=('system.athena.athenad', 'athenad'))
      proc.start()
      proc.join()
      cloudlog.event("athenad exited", exitcode=proc.exitcode)
      time.sleep(5)
  except Exception:
    cloudlog.exception("manage_athenad.exception")
  finally:
    params.remove(ATHENA_MGR_PID_PARAM)


if __name__ == '__main__':
  main()
