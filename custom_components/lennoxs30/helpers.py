"""Support for Lennoxs30 outdoor temperature sensor"""
# pylint: disable=logging-not-lazy
# pylint: disable=logging-fstring-interpolation
# pylint: disable=global-statement
# pylint: disable=broad-except
# pylint: disable=unused-argument
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import logging
from typing import Any

from homeassistant.const import (
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    FREQUENCY_HERTZ,
    ELECTRIC_CURRENT_AMPERE,
    VOLUME_FLOW_RATE_CUBIC_FEET_PER_MINUTE,
    ELECTRIC_POTENTIAL_VOLT,
    TIME_MINUTES,
    TIME_SECONDS,
)

from lennoxs30api import lennox_system
from lennoxs30api.lennox_equipment import lennox_equipment, lennox_equipment_parameter

from . import DOMAIN, Manager


_LOGGER = logging.getLogger(__name__)


def lennox_uom_to_ha_uom(unit: str) -> str:
    """Converts a Lennox UOM to a HASS UOM"""
    if unit == "F":
        return TEMP_FAHRENHEIT
    if unit == "C":
        return TEMP_CELSIUS  # Not validated - do no know if European Units report
    if unit == "CFM":
        return VOLUME_FLOW_RATE_CUBIC_FEET_PER_MINUTE
    if unit == "min":
        return TIME_MINUTES
    if unit == "sec":
        return TIME_SECONDS
    if unit == "%":
        return PERCENTAGE
    if unit == "Hz":
        return FREQUENCY_HERTZ
    if unit == "V":
        return ELECTRIC_POTENTIAL_VOLT
    if unit == "A":
        return ELECTRIC_CURRENT_AMPERE
    if unit == "":
        return None
    return unit


def helper_get_equipment_device_info(manager: Manager, system: lennox_system, equipment_id: int) -> dict:
    """Constructrs the HASS device info for an entity"""
    equip_device_map = manager.system_equip_device_map.get(system.sysId)
    if equip_device_map is not None:
        device = equip_device_map.get(equipment_id)
        if device is not None:
            return {
                "identifiers": {(DOMAIN, device.unique_name)},
            }
        _LOGGER.warning(
            f"helper_get_equipment_device_info Unable to find equipment_id [{equipment_id}] in device map sysId [{system.sysId}], please raise an issue"
        )
    else:
        _LOGGER.error(
            f"helper_get_equipment_device_info No equipment device map found for sysId [{system.sysId}] equipment_id [{equipment_id}], please raise an issue"
        )
    return {
        "identifiers": {(DOMAIN, system.unique_id)},
    }


def helper_create_equipment_entity_name(
    system: lennox_system, equipment: lennox_equipment, name: str, prefix: str = None
) -> str:
    """Creates a name for the entity"""
    suffix = str(equipment.equipment_name)
    if equipment.equipment_id == 1:
        suffix = "ou"
    elif equipment.equipment_id == 2:
        suffix = "iu"
    elif equipment.equipment_id == 0:
        suffix = None

    result: str = system.name

    if prefix is not None:
        result = result + "_" + prefix

    if suffix is not None:
        result = result + "_" + suffix

    result = result + "_" + name

    result = result.replace(" ", "_").replace("-", "").replace(".", "").replace("__", "_")

    return result


def helper_create_system_unique_id(system: lennox_system, suffix: str) -> str:
    """Constructs a unique name for a system entity"""
    result = system.unique_id + suffix
    return result.replace(" ", "_").replace("-", "").replace(".", "").replace("__", "_")


def helper_get_parameter_extra_attributes(equipment: lennox_equipment, parameter: lennox_equipment_parameter):
    """Constructs extra attributes for equipment"""
    attrs: dict[str, Any] = {}
    attrs["equipment_id"] = equipment.equipment_id
    attrs["equipment_type_id"] = equipment.equipType
    attrs["parameter_id"] = parameter.pid
    return attrs
