# encoding: utf-8

import pytest


CRC1153_PLUGINS = (
    "crc1153_layout",
    "crc1153_system_stats",
    "crc1153_search",
    "crc1153_specific_metadata",
    "crc1153_dcat_profile",
)


@pytest.mark.ckan_config("ckan.plugins", " ".join(CRC1153_PLUGINS))
@pytest.mark.usefixtures("with_plugins")
def test_enabled_plugin_entrypoints_load():
    import ckan.plugins as plugins

    for plugin_name in CRC1153_PLUGINS:
        assert plugins.plugin_loaded(plugin_name)


@pytest.mark.ckan_config(
    "ckan.plugins",
    "crc1153_layout crc1153_specific_metadata",
)
@pytest.mark.ckan_config("SECRET_KEY", "test_secret")
@pytest.mark.usefixtures("with_plugins")
def test_sfb_base_asset_include_without_unknown_assets(app, caplog):
    import logging

    from ckan.lib.webassets_tools import include_asset

    caplog.set_level(logging.ERROR, logger="ckan.lib.webassets_tools")

    with app.flask_app.test_request_context("/"):
        include_asset("ckanext-crc1153-layout/sfb1153-js")

    assert "Trying to include unknown asset" not in caplog.text
    assert "vendor/jquery.ui.core" not in caplog.text


def test_search_plugin_uses_ckan_210_callback_names():
    from ckanext.crc1153.plugins.crc_search import CrcSearchPlugin

    plugin = CrcSearchPlugin()

    assert hasattr(plugin, "after_dataset_search")
    assert hasattr(plugin, "after_resource_create")
    assert hasattr(plugin, "before_resource_delete")


def test_layout_plugin_registers_new_activities_helper():
    from ckanext.crc1153.plugins.layout import CrcLayoutPlugin

    helpers = CrcLayoutPlugin().get_helpers()

    assert "new_activities" in helpers


def test_dcat_profile_plugin_uses_ckan_210_callback_names():
    from ckanext.crc1153.plugins.crc_profile import Dcatapcrc1153Plugin

    plugin = Dcatapcrc1153Plugin()

    assert hasattr(plugin, "after_dataset_create")
    assert hasattr(plugin, "after_resource_update")
    assert hasattr(plugin, "before_resource_delete")


def test_specific_metadata_schema_keeps_dataset_and_resource_fields(monkeypatch):
    from ckanext.crc1153.libs.crc_specific_metadata.helpers import (
        CrcSpecificMetadataHelpers,
    )

    monkeypatch.setattr(
        "ckanext.crc1153.libs.crc_specific_metadata.helpers.toolkit.get_validator",
        lambda name: name,
    )
    monkeypatch.setattr(
        "ckanext.crc1153.libs.crc_specific_metadata.helpers.toolkit.get_converter",
        lambda name: name,
    )

    schema = {"resources": {}}
    schema = CrcSpecificMetadataHelpers.updateDatasetSchema(schema)
    schema = CrcSpecificMetadataHelpers.updateResourceSchema(schema)

    assert schema["sfb_dataset_type"] == ["ignore_missing", "convert_to_extras"]
    for field in (
        "material_combination",
        "demonstrator",
        "manufacturing_process",
        "analysis_method",
        "is_automated_processed",
    ):
        assert schema["resources"][field] == ["ignore_missing"]
