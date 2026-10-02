# encoding: utf-8

import pytest
from types import SimpleNamespace

import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
from bs4 import BeautifulSoup
from ckan.tests import factories

from ckanext.crc1153.libs.crc_specific_metadata.helpers import (
    CrcSpecificMetadataHelpers,
)


CRC1153_PLUGINS = (
    "crc1153_layout",
    "crc1153_system_stats",
    "crc1153_search",
    "crc1153_specific_metadata",
    "crc1153_dcat_profile",
)


@pytest.fixture
def csrf_enforced_app(app, with_plugins, monkeypatch):
    flask_app = app.flask_app
    csrf = flask_app.extensions["csrf"]
    blueprint = flask_app.blueprints["crc1153_specific_metadata"]
    monkeypatch.setitem(flask_app.config, "WTF_CSRF_ENABLED", True)
    monkeypatch.setitem(flask_app.config, "WTF_CSRF_CHECK_DEFAULT", True)
    monkeypatch.setitem(h.helper_functions, "cancel_dataset_is_enabled", lambda: False)
    hooks = flask_app.before_request_funcs.setdefault(blueprint.name, [])
    protect = csrf.protect
    hooks.insert(0, protect)
    yield app
    hooks.remove(protect)


def _metadata_payload(dataset_name, csrf_token=None):
    data = {
        "pkg_name": dataset_name,
        "resources_count": "0",
        "processed_metadata_material_combination": "0",
        "processed_metadata_demonstrator": "0",
        "processed_metadata_manufacturing_process": "0",
        "processed_metadata_analysis_method": "0",
    }
    if csrf_token:
        data["_csrf_token"] = csrf_token
    return data


@pytest.mark.ckan_config(
    "ckan.plugins", "crc1153_specific_metadata crc1153_layout"
)
@pytest.mark.ckan_config("SECRET_KEY", "test_secret")
def test_specific_metadata_form_contains_csrf_token(
    csrf_enforced_app, clean_db, monkeypatch
):
    user = factories.Sysadmin()
    dataset = factories.Dataset(user=user)
    monkeypatch.setattr(CrcSpecificMetadataHelpers, "get_material_list", lambda: [])
    monkeypatch.setattr(
        CrcSpecificMetadataHelpers, "get_demonstrator_list", lambda: []
    )

    response = csrf_enforced_app.get(
        "/resource_custom_metadata/add_metadata/{}".format(dataset["name"]),
        extra_environ={"REMOTE_USER": user["name"]},
    )

    assert response.status_code == 200
    document = BeautifulSoup(response.get_data(as_text=True), "html.parser")
    form = document.select_one("#resource-custom-metadata-form")
    csrf_input = form.select_one('input[name="_csrf_token"]')
    assert csrf_input is not None
    assert csrf_input.attrs["value"]


@pytest.mark.ckan_config(
    "ckan.plugins", "crc1153_specific_metadata crc1153_layout"
)
@pytest.mark.ckan_config("SECRET_KEY", "test_secret")
def test_save_specific_metadata_requires_csrf_token(csrf_enforced_app, clean_db):
    user = factories.Sysadmin()
    dataset = factories.Dataset(user=user)

    response = csrf_enforced_app.post(
        "/resource_custom_metadata/save_metadata",
        data=_metadata_payload(dataset["name"]),
        extra_environ={"REMOTE_USER": user["name"]},
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert "The CSRF token is missing." in response.get_data(as_text=True)


@pytest.mark.ckan_config(
    "ckan.plugins", "crc1153_specific_metadata crc1153_layout"
)
@pytest.mark.ckan_config("SECRET_KEY", "test_secret")
def test_save_specific_metadata_accepts_rendered_token_and_preserves_behavior(
    csrf_enforced_app, clean_db, monkeypatch
):
    user = factories.Sysadmin()
    dataset = factories.Dataset(
        user=user,
        resources=[{"url": "https://example.test/data.csv", "name": "data.csv"}]
    )
    resource = dataset["resources"][0]
    monkeypatch.setattr(CrcSpecificMetadataHelpers, "get_material_list", lambda: [])
    monkeypatch.setattr(
        CrcSpecificMetadataHelpers, "get_demonstrator_list", lambda: []
    )
    real_get_action = toolkit.get_action

    def get_action(name):
        action = real_get_action(name)
        if name != "resource_update":
            return action

        def tracked_resource_update(context, data_dict):
            result = action(context, data_dict)
            updated_resources.append(dict(data_dict))
            return result

        return tracked_resource_update

    updated_resources = []
    monkeypatch.setattr(toolkit, "get_action", get_action)
    client = csrf_enforced_app.test_client()
    auth = {"REMOTE_USER": user["name"]}
    form_response = client.get(
        "/resource_custom_metadata/add_metadata/{}".format(dataset["name"]),
        extra_environ=auth,
    )
    document = BeautifulSoup(form_response.get_data(as_text=True), "html.parser")
    csrf_input = document.select_one('input[name="_csrf_token"]')
    data = _metadata_payload(dataset["name"], csrf_input.attrs["value"])
    data.update(
        {
            "resources_count": "1",
            "material_combination_1": "Steel, Aluminum",
            "custom_metadata_material_combination_1": resource["id"],
        }
    )

    response = client.post(
        "/resource_custom_metadata/save_metadata",
        data=data,
        extra_environ=auth,
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.location.endswith("/dataset/{}".format(dataset["name"]))
    assert len(updated_resources) == 1
    assert updated_resources[0]["id"] == resource["id"]
    assert updated_resources[0]["material_combination"] == "Steel, Aluminum"
    saved_resource = real_get_action("resource_show")(
        {"ignore_auth": True}, {"id": resource["id"]}
    )
    assert saved_resource["material_combination"] == "Steel, Aluminum"


@pytest.mark.ckan_config("ckan.plugins", " ".join(CRC1153_PLUGINS))
@pytest.mark.usefixtures("with_plugins")
def test_enabled_plugin_entrypoints_load():
    import ckan.plugins as plugins

    for plugin_name in CRC1153_PLUGINS:
        assert plugins.plugin_loaded(plugin_name)


def test_system_stats_registers_only_its_existing_template_directory(
    monkeypatch,
):
    from ckanext.crc1153.plugins.system_stats import SystemStatsPlugin

    registered_templates = []
    monkeypatch.setattr(
        "ckanext.crc1153.plugins.system_stats.toolkit.add_template_directory",
        lambda config, path: registered_templates.append((config, path)),
    )
    monkeypatch.setattr(
        "ckanext.crc1153.plugins.system_stats.toolkit.add_public_directory",
        lambda *_args: pytest.fail("system stats has no public directory"),
    )
    monkeypatch.setattr(
        "ckanext.crc1153.plugins.system_stats.toolkit.add_resource",
        lambda *_args: pytest.fail("system stats has no webassets bundle"),
    )

    config = {}
    SystemStatsPlugin().update_config(config)

    assert registered_templates == [(config, "../templates")]


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
@pytest.mark.parametrize(
    "userobj,expected_text",
    [
        (None, "account not-authed"),
        (
            SimpleNamespace(
                id="normal-user-id",
                name="normal-user",
                display_name="Normal User",
                sysadmin=False,
            ),
            "/dashboard/datasets",
        ),
        (
            SimpleNamespace(
                id="sysadmin-user-id",
                name="sysadmin-user",
                display_name="Sysadmin User",
                sysadmin=True,
            ),
            "/dashboard/datasets",
        ),
    ],
)
def test_sfb_header_renders_without_dashboard_build_error(
    app, monkeypatch, userobj, expected_text
):
    from ckan.lib.base import render
    from flask import Response

    from ckanext.crc1153.libs.crc_layout import helpers

    def get_action(name):
        assert name != "dashboard_new_activities_count"
        raise KeyError(name)

    monkeypatch.setattr(helpers, "c", SimpleNamespace(userobj=userobj))
    monkeypatch.setattr(helpers.toolkit, "get_action", get_action)

    with app.flask_app.test_request_context("/"):
        from flask import g

        g.userobj = userobj
        g.user = userobj.name if userobj else ""
        response = Response(render("header.html", {}))

    assert response.status_code == 200
    assert expected_text in response.get_data(as_text=True)
    assert "activity.dashboard" not in response.get_data(as_text=True)


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
