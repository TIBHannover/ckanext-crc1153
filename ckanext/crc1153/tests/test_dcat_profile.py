# encoding: utf-8

from rdflib import Graph, Literal, URIRef


DATASET_REF = URIRef("http://example.com/dataset/dataset-1")
RESOURCE_REF = URIRef("http://example.com/dataset/dataset-1/resource/resource-1")


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
