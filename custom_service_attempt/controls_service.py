from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.int import Uint8Characteristic
from adafruit_ble.services import Service

class ControlsService(Service):
    uuid = VendorUUID("77791967-b5c7-4a0f-842f-d28bfa439742")

    # Example characteristics
    speed = Uint8Characteristic(
        uuid=VendorUUID("77791967-b5c7-4a0f-842f-d28bfa439742"),
        properties=Characteristic.READ,
        initial_value=7
    )
