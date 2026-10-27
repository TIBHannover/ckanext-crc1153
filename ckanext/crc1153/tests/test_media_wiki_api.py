# encoding: utf-8

import logging

from requests import exceptions as requests_exceptions


def test_mediawiki_defaults_point_to_sfb1153_smw(monkeypatch):
    from ckanext.crc1153.libs import media_wiki_api

    created = {}

    class FakeSite:
        def __init__(self, **kwargs):
            created.update(kwargs)

        def ask(self, query):
            return [{"fulltext": "Aluminium"}]

    monkeypatch.setattr(media_wiki_api.AuthHelpers, "get_mediaWiki_creds", lambda: {})
    monkeypatch.setattr(media_wiki_api, "Site", FakeSite)

    results = media_wiki_api.MediaWikiAPI(
        query="[[Category:SampleMaterial]]",
        query_type="material",
    ).pipeline()

    assert created["scheme"] == "https"
    assert created["host"] == "smw.service.tib.eu"
    assert created["path"] == "/wiki-sfb1153/"
    assert created["reqs"] == {"timeout": 30}
    assert results == ["Aluminium"]


def test_mediawiki_config_overrides_host_path_and_timeout(monkeypatch):
    from ckanext.crc1153.libs import media_wiki_api

    created = {}

    class FakeSite:
        def __init__(self, **kwargs):
            created.update(kwargs)

        def ask(self, query):
            return [{"fulltext": "Steel"}]

    monkeypatch.setattr(media_wiki_api.AuthHelpers, "get_mediaWiki_creds", lambda: {})
    monkeypatch.setattr(media_wiki_api, "Site", FakeSite)
    monkeypatch.setitem(
        media_wiki_api.toolkit.config,
        "ckanext.crc1153.mediawiki.host",
        "example.test",
    )
    monkeypatch.setitem(
        media_wiki_api.toolkit.config,
        "ckanext.crc1153.mediawiki.path",
        "/custom-wiki/",
    )
    monkeypatch.setitem(
        media_wiki_api.toolkit.config,
        "ckanext.crc1153.mediawiki.timeout",
        "5",
    )

    assert media_wiki_api.MediaWikiAPI("query", query_type="material").pipeline()
    assert created["host"] == "example.test"
    assert created["path"] == "/custom-wiki/"
    assert created["reqs"] == {"timeout": 5}


def test_sfb1368_uses_shared_smw_connection_settings(monkeypatch):
    from ckanext.crc1153.libs import media_wiki_api

    monkeypatch.setattr(media_wiki_api.AuthHelpers, "get_mediaWiki_creds", lambda: {})
    monkeypatch.setitem(media_wiki_api.toolkit.config, "ckanext.crc.project.id", "1368")
    monkeypatch.setitem(
        media_wiki_api.toolkit.config,
        "ckanext.smw.mediawiki.api.endpoint",
        "wiki.example",
    )
    monkeypatch.setitem(
        media_wiki_api.toolkit.config,
        "ckanext.smw.mediawiki.api.path",
        "/wiki-sfb1368/",
    )
    monkeypatch.setitem(
        media_wiki_api.toolkit.config,
        "ckanext.smw.mediawiki.api.scheme",
        "http",
    )

    api = media_wiki_api.MediaWikiAPI("query")

    assert (api.host, api.path, api.scheme) == (
        "wiki.example",
        "/wiki-sfb1368/",
        "http",
    )


def test_demonstrator_response_uses_requested_smw_property(monkeypatch):
    from ckanext.crc1153.libs import media_wiki_api

    monkeypatch.setattr(media_wiki_api.AuthHelpers, "get_mediaWiki_creds", lambda: {})
    api = media_wiki_api.MediaWikiAPI("query", query_type="demonstrator")

    assert api.process_answer(
        "demonstrator",
        {"printouts": {"RepresentsDemonstrator": [{"fulltext": "Demo A"}]}},
    ) == "Demo A"


def test_mediawiki_failure_is_logged_without_sensitive_response(monkeypatch, caplog):
    from ckanext.crc1153.libs import media_wiki_api

    class FakeSite:
        def __init__(self, **kwargs):
            pass

        def ask(self, query):
            raise requests_exceptions.Timeout("secret response body")

    monkeypatch.setattr(media_wiki_api.AuthHelpers, "get_mediaWiki_creds", lambda: {})
    monkeypatch.setattr(media_wiki_api, "Site", FakeSite)

    with caplog.at_level(logging.WARNING):
        results = media_wiki_api.MediaWikiAPI("query").pipeline()

    assert results == []
    assert "MediaWiki query failed" in caplog.text
    assert "secret response body" not in caplog.text
