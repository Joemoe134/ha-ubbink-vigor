"""DataUpdateCoordinator for Ubbink Vigor."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .modbus_client import UbbinkModbusClient

_LOGGER = logging.getLogger(__name__)

# After this many consecutive failures the coordinator backs off to a
# slower poll interval so it does not spam the logs / network.
MAX_FAILURES_BEFORE_BACKOFF = 3
BACKOFF_INTERVAL = 120  # seconds


class UbbinkVigorCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data fetching from the Vigor unit."""

    def __init__(self, hass: HomeAssistant, client: UbbinkModbusClient) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client
        self._consecutive_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Vigor unit."""
        # Reconnect if needed (TCP dropped, Pi Zero rebooted, etc.)
        if not self.client.connected:
            _LOGGER.debug("Modbus client disconnected, attempting reconnect")
            connected = await self.client.connect()
            if not connected:
                self._consecutive_failures += 1
                self._maybe_backoff()
                raise UpdateFailed(
                    "Cannot connect to Ubbink Vigor – check bridge device"
                )

        data = await self.client.read_all_data()
        if data is None:
            self._consecutive_failures += 1
            self._maybe_backoff()
            # Try to reconnect on next cycle
            await self.client.close()
            raise UpdateFailed("Failed to read data from Ubbink Vigor")

        # Successful read – reset failure counter and restore normal interval
        if self._consecutive_failures > 0:
            _LOGGER.info("Ubbink Vigor communication restored")
            self._consecutive_failures = 0
            self.update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

        return data

    def _maybe_backoff(self) -> None:
        """Slow down polling after repeated failures."""
        if self._consecutive_failures >= MAX_FAILURES_BEFORE_BACKOFF:
            if self.update_interval != timedelta(seconds=BACKOFF_INTERVAL):
                _LOGGER.warning(
                    "Ubbink Vigor unreachable after %s attempts, "
                    "backing off to %ss poll interval",
                    self._consecutive_failures,
                    BACKOFF_INTERVAL,
                )
                self.update_interval = timedelta(seconds=BACKOFF_INTERVAL)
