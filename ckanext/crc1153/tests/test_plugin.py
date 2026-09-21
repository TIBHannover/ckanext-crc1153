# encoding: utf-8

import pytest
from types import SimpleNamespace


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


@pytest.mark.ckan_config("ckan.plugins", "crc1153_layout")
@pytest.mark.usefixtures("with_plugins")
def test_sfb_header_renders_for_logged_out_users_without_activity_action(app, monkeypatch):
    from ckan.lib.base import render

    from ckanext.crc1153.libs.crc_layout import helpers

    monkeypatch.setattr(helpers, "c", SimpleNamespace(userobj=None))

    def get_action(name):
        raise AssertionError("logged-out header must not request actions")

    monkeypatch.setattr(helpers.toolkit, "get_action", get_action)

    with app.flask_app.test_request_context("/"):
        header = render("header.html", {})

    assert "account not-authed" in header


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


def test_new_activities_returns_zero_for_logged_out_users(monkeypatch):
    from ckanext.crc1153.libs.crc_layout import helpers

    monkeypatch.setattr(helpers, "c", SimpleNamespace(userobj=None))

    def get_action(name):
        raise AssertionError("logged-out users should not request actions")

    monkeypatch.setattr(helpers.toolkit, "get_action", get_action)

    assert helpers.Helper.new_activities() == 0


def test_new_activities_uses_dashboard_activity_list_without_old_count_action(monkeypatch):
    from ckanext.crc1153.libs.crc_layout import helpers

    monkeypatch.setattr(
        helpers,
        "c",
        SimpleNamespace(userobj=SimpleNamespace(id="user-id", name="user-name")),
    )
    requested_actions = []

    def get_action(name):
        requested_actions.append(name)
        assert name != "dashboard_new_activities_count"
        assert name == "dashboard_activity_list"

        def dashboard_activity_list(context, data_dict):
            assert context["user"] == "user-id"
            return [
                {"is_new": True},
                {"is_new": False},
                {"is_new": True},
            ]

        return dashboard_activity_list

    monkeypatch.setattr(helpers.toolkit, "get_action", get_action)

    assert helpers.Helper.new_activities() == 2
    assert requested_actions == ["dashboard_activity_list"]


def test_new_activities_returns_zero_when_activity_action_is_unavailable(monkeypatch):
    from ckanext.crc1153.libs.crc_layout import helpers

    monkeypatch.setattr(
        helpers,
        "c",
        SimpleNamespace(userobj=SimpleNamespace(id="user-id")),
    )

    def get_action(name):
        assert name != "dashboard_new_activities_count"
        raise KeyError(name)

    monkeypatch.setattr(helpers.toolkit, "get_action", get_action)

    assert helpers.Helper.new_activities() == 0


@pytest.mark.parametrize("error", ["not_authorized", "unexpected"])
def test_new_activities_returns_zero_when_activity_action_fails(monkeypatch, error):
    from ckanext.crc1153.libs.crc_layout import helpers

    monkeypatch.setattr(
        helpers,
        "c",
        SimpleNamespace(userobj=SimpleNamespace(id="user-id")),
    )

    def get_action(name):
        assert name != "dashboard_new_activities_count"

        def dashboard_activity_list(context, data_dict):
            if error == "not_authorized":
                raise helpers.toolkit.NotAuthorized()
            raise RuntimeError("activity failure")

        return dashboard_activity_list

    monkeypatch.setattr(helpers.toolkit, "get_action", get_action)

    assert helpers.Helper.new_activities() == 0


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
