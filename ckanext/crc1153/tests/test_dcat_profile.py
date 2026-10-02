# encoding: utf-8

import logging
from unittest.mock import Mock

import pytest
import ckan.plugins as plugins
from ckan.common import CKANConfig
from ckan.config.declaration import Declaration, Key
from rdflib import Graph, Literal, URIRef

from ckanext.crc1153.libs.crc_profile import helpers
from ckanext.crc1153.libs.crc_profile.helpers import Crc1153DcatProfileHelper
from ckanext.crc1153.plugins.crc_profile import Dcatapcrc1153Plugin


DATASET_REF = URIRef("http://example.com/dataset/dataset-1")
RESOURCE_REF = URIRef("http://example.com/dataset/dataset-1/resource/resource-1")
CANONICAL_JENA_KEY = "ckanext.crc1153.apachejena.endpoint"
SHARED_JENA_KEY = "ckanext.apachejena.endpoint"
HISTORICAL_JENA_KEY = "ckanext.apacheJena.endpoint"
CANONICAL_CREDENTIALS_KEY = "ckanext.crc1153.mediawiki_credentials_path"
SHARED_CREDENTIALS_KEY = "ckanext.mediawiki_credentials_path"


def _declared_config(values):
    declaration = Declaration()
    Dcatapcrc1153Plugin().declare_config_options(declaration, Key())
    config = CKANConfig(values)
    declaration.make_safe(config)
    return declaration, config


@pytest.mark.ckan_config("ckan.plugins", "crc1153_dcat_profile")
@pytest.mark.usefixtures("with_plugins")
def test_canonical_jena_endpoint_is_declared(ckan_config, caplog):
    assert ckan_config.is_declared(CANONICAL_JENA_KEY)
    ckan_config.get(CANONICAL_JENA_KEY)
    assert f"Option {CANONICAL_JENA_KEY} is not declared" not in caplog.text


def test_plugin_declares_only_crc1153_owned_config():
    assert plugins.IConfigDeclaration.implemented_by(Dcatapcrc1153Plugin)
    declaration = Declaration()
    Dcatapcrc1153Plugin().declare_config_options(declaration, Key())

    assert declaration.get(SHARED_JENA_KEY).legacy_key == HISTORICAL_JENA_KEY
    assert declaration.get(CANONICAL_JENA_KEY).legacy_key == SHARED_JENA_KEY
    assert declaration.get(CANONICAL_CREDENTIALS_KEY).legacy_key == (
        SHARED_CREDENTIALS_KEY
    )
    assert declaration.get(SHARED_CREDENTIALS_KEY).legacy_key == (
        "ckanext.mediaWiki_credentials_path"
    )


def test_canonical_jena_endpoint_is_used(monkeypatch):
    declaration, config = _declared_config(
        {CANONICAL_JENA_KEY: "https://jena.example.test/canonical"}
    )
    monkeypatch.setattr(helpers.toolkit, "config", config)

    assert declaration.get(SHARED_JENA_KEY).legacy_key == HISTORICAL_JENA_KEY
    assert declaration.get(CANONICAL_JENA_KEY).legacy_key == SHARED_JENA_KEY
    assert Crc1153DcatProfileHelper.get_apache_jena_endpoint() == (
        "https://jena.example.test/canonical"
    )


def test_shared_jena_endpoint_populates_canonical_key(monkeypatch, caplog):
    with caplog.at_level(logging.WARNING, logger="ckan.config.declaration"):
        _, config = _declared_config(
            {SHARED_JENA_KEY: "https://jena.example.test/shared"}
        )
    monkeypatch.setattr(helpers.toolkit, "config", config)

    assert config[CANONICAL_JENA_KEY] == "https://jena.example.test/shared"
    assert Crc1153DcatProfileHelper.get_apache_jena_endpoint() == (
        "https://jena.example.test/shared"
    )
    assert (
        f"Config option '{SHARED_JENA_KEY}' is deprecated. "
        f"Use '{CANONICAL_JENA_KEY}' instead"
    ) in caplog.text


def test_historical_jena_endpoint_remains_supported(monkeypatch, caplog):
    _, config = _declared_config(
        {HISTORICAL_JENA_KEY: "https://jena.example.test/historical"}
    )
    monkeypatch.setattr(helpers.toolkit, "config", config)

    assert Crc1153DcatProfileHelper.get_apache_jena_endpoint() == (
        "https://jena.example.test/historical"
    )
    assert HISTORICAL_JENA_KEY in caplog.text


def test_canonical_jena_endpoint_takes_precedence_over_shared(monkeypatch):
    _, config = _declared_config(
        {
            CANONICAL_JENA_KEY: "https://jena.example.test/canonical",
            SHARED_JENA_KEY: "https://jena.example.test/shared",
        }
    )
    monkeypatch.setattr(helpers.toolkit, "config", config)

    assert Crc1153DcatProfileHelper.get_apache_jena_endpoint() == (
        "https://jena.example.test/canonical"
    )


def test_shared_jena_endpoint_takes_precedence_over_historical(monkeypatch):
    _, config = _declared_config(
        {
            SHARED_JENA_KEY: "https://jena.example.test/shared",
            HISTORICAL_JENA_KEY: "https://jena.example.test/historical",
        }
    )
    monkeypatch.setattr(helpers.toolkit, "config", config)

    assert Crc1153DcatProfileHelper.get_apache_jena_endpoint() == (
        "https://jena.example.test/shared"
    )


def test_missing_jena_endpoint_still_skips_sparql_writes(monkeypatch):
    _, config = _declared_config({})
    monkeypatch.setattr(helpers.toolkit, "config", config)
    sparql_wrapper = Mock()
    monkeypatch.setattr(helpers, "SPARQLWrapper", sparql_wrapper)
    graph = Graph()
    graph.add((DATASET_REF, URIRef("https://schema.org/name"), Literal("Dataset")))

    assert Crc1153DcatProfileHelper.insert_to_sparql(graph) is None
    assert Crc1153DcatProfileHelper.delete_from_sparql(graph) is None
    sparql_wrapper.assert_not_called()


def test_crc1153_dcat_profile_generates_crc_specific_triples(monkeypatch):
    from ckanext.crc1153.profiles import crc_profile
    from ckanext.crc1153.profiles.crc_profile import CRC1153DCATAPProfile

    monkeypatch.setattr(
        crc_profile.Helper,
        "get_linked_publication",
        lambda dataset_name: ["Important publication"],
    )
    monkeypatch.setattr(
        crc_profile.Helper,
        "get_linked_machines",
        lambda resource_id: {"Machine A": "http://example.com/machine/a"},
    )
    monkeypatch.setattr(
        crc_profile.Helper,
        "get_linked_samples",
        lambda resource_id: {"Sample A": "http://example.com/sample/a"},
    )
    monkeypatch.setattr(
        crc_profile,
        "resource_uri",
        lambda resource_dict: str(RESOURCE_REF),
    )

    graph = Graph()
    profile = CRC1153DCATAPProfile(graph)
    profile.graph_from_dataset(
        {
            "name": "dataset-1",
            "sfb_dataset_type": "Publication Related",
            "resources": [
                {
                    "id": "resource-1",
                    "material_combination": "Steel",
                    "manufacturing_process": "Rolling",
                    "demonstrator": "Demo",
                    "analysis_method": "Microscopy",
                }
            ],
        },
        DATASET_REF,
    )

    assert (
        DATASET_REF,
        URIRef("https://schema.org/citation"),
        Literal("Important publication"),
    ) in graph
    assert (
        DATASET_REF,
        URIRef("http://purl.org/dc/terms/Type"),
        Literal("Publication Related"),
    ) in graph
    assert (
        RESOURCE_REF,
        URIRef("http://emmo.info/emmo/Material"),
        Literal("Steel"),
    ) in graph
    assert (
        RESOURCE_REF,
        URIRef("http://emmo.info/emmo/Device"),
        URIRef("http://example.com/machine/a"),
    ) in graph


def test_crc1153_rdf_profile_is_added_to_serializer_profiles(monkeypatch):
    from ckanext.crc1153.libs.crc_profile.helpers import Crc1153DcatProfileHelper

    monkeypatch.setattr(
        "ckanext.crc1153.libs.crc_profile.helpers.toolkit.config",
        {"ckanext.dcat.rdf.profiles": "euro_dcat_ap_2"},
    )

    assert Crc1153DcatProfileHelper.get_rdf_profiles() == [
        "euro_dcat_ap_2",
        "crc1153_dcat_ap",
    ]
