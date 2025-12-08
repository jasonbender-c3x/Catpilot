import os
from typing import cast

from catpilot.system.hardware.base import HardwareBase
from catpilot.system.hardware.tici.hardware import Tici
from catpilot.system.hardware.pc.hardware import Pc

TICI = os.path.isfile('/TICI')
AGNOS = os.path.isfile('/AGNOS')
PC = not TICI


if TICI:
  HARDWARE = cast(HardwareBase, Tici())
else:
  HARDWARE = cast(HardwareBase, Pc())
