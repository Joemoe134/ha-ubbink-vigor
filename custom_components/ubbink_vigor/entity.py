"""Base entity for Ubbink Vigor."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import UbbinkVigorCoordinator


class UbbinkVigorEntity(CoordinatorEntity[UbbinkVigorCoordinator]):
    """Base class for Ubbink Vigor entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: UbbinkVigorCoordinator, key: str) -> None:
        """Initialise the entity."""
        super().__init__(coordinator)
        serial = coordinator.data.get("serial_number", "unknown")
        self._attr_unique_id = f"{serial}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        serial = self.coordinator.data.get("serial_number", "unknown")
        return DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name="Ubbink Vigor",
            manufacturer=MANUFACTURER,
            model="Ubiflux Vigor W400",
            serial_number=serial,
            sw_version=None,
        )
