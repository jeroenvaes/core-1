"""Setup NikoHomeControlFan."""
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import percentage_to_ordered_list_item

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Niko Home Control fan platform."""
    hub = hass.data[DOMAIN][entry.entry_id]["hub"]
    enabled_entities = hass.data[DOMAIN][entry.entry_id]["enabled_entities"]
    if enabled_entities["fans"] is False:
        return

    entities: list[NikoHomeControlFan] = []

    for action in hub.actions:
        entity = None
        action_type = action.action_type
        if action_type == 3:
            NikoHomeControlFan(action, hub, options=entry.data["options"])

        if entity:
            hub.entities.append(entity)
            entities.append(entity)

    async_add_entities(entities, True)


class NikoHomeControlFan(FanEntity):
    """Representation of an Niko fan."""

    def __init__(self, action, hub, options):
        """Set up the Niko Home Control action platform."""
        self._hub = hub
        self._action = action
        self._attr_name = action.name
        self._attr_is_on = action.is_on
        self._attr_unique_id = f"fan-{action.action_id}"
        self._fan_speed = action.state
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._preset_modes = ["low", "medium", "high", "very_high"]

        if options["treatAsDevice"] is not False:
            self._attr_device_info = {
                "identifiers": {(DOMAIN, self._attr_unique_id)},
                "manufacturer": "Niko",
                "name": action.name,
                "model": "P.O.M",
                "via_device": hub._via_device,
            }
            if options["importLocations"] is not False:
                self._attr_device_info["suggested_area"] = action.location
        else:
            self._attr_device_info = hub._device_info

    @property
    def should_poll(self) -> bool:
        """No polling needed for a Niko light."""
        return False

    @property
    def id(self):
        """A Niko Action action_id."""
        return self._action.action_id

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode."""
        return self._fan_speed

    @property
    def supported_features(self):
        """Return supported features."""
        return self._attr_supported_features

    def set_percentage(self, percentage: int) -> None:
        """Set the fan speed preset based on a given percentage."""
        mode = percentage_to_ordered_list_item(self._preset_modes, percentage)
        if mode == "low":
            self._action.set_fan_speed(0)
        elif mode == "medium":
            self._action.set_fan_speed(1)
        elif mode == "high":
            self._action.set_fan_speed(2)
        elif mode == "very_high":
            self._action.set_fan_speed(3)

        self.schedule_update_ha_state()

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        if preset_mode == "low":
            self._action.set_fan_speed(0)
        elif preset_mode == "medium":
            self._action.set_fan_speed(1)
        elif preset_mode == "high":
            self._action.set_fan_speed(2)
        elif preset_mode == "very_high":
            self._action.set_fan_speed(3)

        self.schedule_update_ha_state()

    def update_state(self, state):
        """Update HA state."""
        self._fan_speed = state
        self.schedule_update_ha_state()
