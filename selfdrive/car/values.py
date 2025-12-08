from typing import get_args
from catpilot.selfdrive.car.body.values import CAR as BODY
from catpilot.selfdrive.car.chrysler.values import CAR as CHRYSLER
from catpilot.selfdrive.car.ford.values import CAR as FORD
from catpilot.selfdrive.car.gm.values import CAR as GM
from catpilot.selfdrive.car.honda.values import CAR as HONDA
from catpilot.selfdrive.car.hyundai.values import CAR as HYUNDAI
from catpilot.selfdrive.car.mazda.values import CAR as MAZDA
from catpilot.selfdrive.car.mock.values import CAR as MOCK
from catpilot.selfdrive.car.nissan.values import CAR as NISSAN
from catpilot.selfdrive.car.subaru.values import CAR as SUBARU
from catpilot.selfdrive.car.tesla.values import CAR as TESLA
from catpilot.selfdrive.car.toyota.values import CAR as TOYOTA
from catpilot.selfdrive.car.volkswagen.values import CAR as VOLKSWAGEN

Platform = BODY | CHRYSLER | FORD | GM | HONDA | HYUNDAI | MAZDA | MOCK | NISSAN | SUBARU | TESLA | TOYOTA | VOLKSWAGEN
BRANDS = get_args(Platform)

PLATFORMS: dict[str, Platform] = {str(platform): platform for brand in BRANDS for platform in brand}
