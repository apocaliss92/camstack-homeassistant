"""CamStack integration for Home Assistant."""

import logging
import os

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PANEL_FILENAME, PANEL_NAME, PANEL_URL
from .frontend import async_register_card

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the CamStack component."""
    async def _register_card(_=None) -> None:
        await async_register_card(hass)

    if hass.state == CoreState.running:
        await _register_card()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _register_card)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CamStack from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    config = {**entry.data, **entry.options}
    hass.data[DOMAIN][entry.entry_id] = {"config": config, "options": entry.options}

    await _register_frontend(hass, entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    frontend.async_remove_panel(hass, "camstack")

    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        del hass.data[DOMAIN][entry.entry_id]

    return True


def _build_iframe_url(hass: HomeAssistant, config: dict) -> str | None:
    """Build the iframe URL from config."""
    url_base = (config.get("url_base") or "").strip().rstrip("/")
    _LOGGER.debug("CamStack _build_iframe_url: url_base=%r", url_base)
    if not url_base:
        _LOGGER.warning("CamStack: url_base empty, panel will not be registered")
        return None

    if url_base.startswith("/"):
        base = hass.config.internal_url or "http://homeassistant.local:8123"
        result = f"{base.rstrip('/')}{url_base}"
    else:
        result = url_base
    _LOGGER.info("CamStack panel iframe_url=%s", result)
    return result


async def _register_frontend(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register the CamStack panel."""
    config = {**entry.data, **entry.options}
    iframe_url = _build_iframe_url(hass, config)
    if not iframe_url:
        _LOGGER.warning("CamStack: no iframe_url, skipping panel registration")
        return

    root = os.path.join(hass.config.path("custom_components"), DOMAIN)
    panel_path = os.path.join(root, "frontend", PANEL_FILENAME)

    if os.path.isfile(panel_path):
        try:
            await hass.http.async_register_static_paths(
                [StaticPathConfig(PANEL_URL, panel_path, cache_headers=False)]
            )
        except RuntimeError as err:
            err_msg = str(err)
            if "already" in err_msg.lower() or "never be executed" in err_msg:
                _LOGGER.debug("Panel path %s already registered: %s", PANEL_URL, err)
            else:
                raise

    await panel_custom.async_register_panel(
        hass,
        "camstack",
        PANEL_NAME,
        sidebar_title=config.get("panel_title", "CamStack"),
        sidebar_icon=config.get("panel_icon", "mdi:cctv"),
        module_url=PANEL_URL,
        embed_iframe=True,
        config={"url": iframe_url},
    )
