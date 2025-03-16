from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)


DOMAIN = "smarthomesec"

INTEGRATION_TITLE = "SmartHomeSec"

API_BASEHOST = "smarthomesec.bydemes.com"
API_BASEPATH = "REST/v2"

TYPE_TRANSLATION = {
    "device_type.door_contact": "Door contact",
    "device_type.keypad": "Keypad",
    "device_type.pir": "Motion detector",
    "device_type.ipcam": "IP camera",
}
TYPE_CLASS_BINARY_SENSOR = {
    "device_type.door_contact": BinarySensorDeviceClass.DOOR,
    "device_type.pir": BinarySensorDeviceClass.MOTION,
}

ALARM_AREAS = ["1"]