import logging

import ckan.plugins.toolkit as toolkit


log = logging.getLogger(__name__)


def get_owned_config_value(canonical_key, *legacy_keys):
    config = toolkit.config
    if canonical_key in config:
        value = config[canonical_key]
        if value is not None:
            return value

    for legacy_key in legacy_keys:
        if legacy_key in config and config[legacy_key] is not None:
            log.warning(
                "Config option '%s' is deprecated. Use '%s' instead",
                legacy_key,
                canonical_key,
            )
            return config[legacy_key]

    return None
