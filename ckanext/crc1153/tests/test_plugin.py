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
@pytest.mark.usefixtures("with_plugins", "with_request_context")
def test_sfb_header_and_resource_form_render(monkeypatch):
    import ckan.lib.helpers as h
    from ckan.lib.base import render_jinja2

    monkeypatch.setattr(
        h,
        "get_material_list_from_smw",
        lambda: [{"value": "Steel", "text": "Steel"}],
    )
    monkeypatch.setattr(
        h,
        "get_demonstrator_list_from_smw",
        lambda: [{"value": "Demo", "text": "Demo"}],
    )

    header = render_jinja2("header.html", {})
    assert "sfb-header-container" in header
    assert "user_manual.help" in header or "Datasets" in header

    resource_form = render_jinja2(
        "package/snippets/resource_form.html",
        {
            "data": {
                "id": "",
                "url": "",
                "url_type": "",
                "name": "",
                "description": "",
                "format": "",
                "material_combination": "Steel",
                "demonstrator": "Demo",
                "manufacturing_process": "",
                "analysis_method": "",
            },
            "errors": {},
            "error_summary": {},
            "pkg_name": "dataset-one",
            "dataset_type": "dataset",
            "stage": [],
            "form_action": "/dataset/dataset-one/resource/new",
            "include_metadata": False,
        },
    )
    assert "material_combination" in resource_form
    assert "demonstrator" in resource_form


def test_search_plugin_uses_ckan_210_callback_names():
    from ckanext.crc1153.plugins.crc_search import CrcSearchPlugin

    plugin = CrcSearchPlugin()

    assert hasattr(plugin, "after_dataset_search")
    assert hasattr(plugin, "after_resource_create")
    assert hasattr(plugin, "before_resource_delete")


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
