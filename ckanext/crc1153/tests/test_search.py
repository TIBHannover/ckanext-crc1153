# encoding: utf-8


def _search_results():
    return {
        "count": 1,
        "results": [{"name": "unchanged"}],
        "search_facets": {
            "organization": {"items": [{"name": "org", "count": 1}]},
            "tags": {"items": []},
            "groups": {"items": []},
        },
    }


def test_normal_search_results_are_unmodified():
    from ckanext.crc1153.plugins.crc_search import CrcSearchPlugin

    plugin = CrcSearchPlugin()
    search_results = _search_results()

    result = plugin.after_dataset_search(search_results, {"q": "normal", "fq": [""]})

    assert result is search_results
    assert result["results"] == [{"name": "unchanged"}]


def test_column_search_is_dispatched(monkeypatch):
    from ckanext.crc1153.plugins import crc_search

    calls = []

    def fake_run(search_query, search_params, search_results):
        calls.append((search_query, search_params))
        search_results["results"] = [{"name": "column-match"}]
        return search_results

    monkeypatch.setattr(crc_search.ColumnSearch, "run", fake_run)

    result = crc_search.CrcSearchPlugin().after_dataset_search(
        _search_results(),
        {"q": "column:force", "fq": [""]},
    )

    assert calls == [("column:force", {"q": "column:force", "fq": [""]})]
    assert result["results"] == [{"name": "column-match"}]


def test_empty_special_searches_are_removed_before_solr():
    from ckanext.crc1153.plugins.crc_search import CrcSearchPlugin

    for search_type in (
        "column", "publication", "sample", "material_combination",
        "demonstrator", "manufacturing_process", "analysis_method",
    ):
        params = {
            "q": search_type + ":   ",
            "fq": ['organization:"sfb1153"'],
            "sort": "metadata_modified desc",
        }

        result = CrcSearchPlugin().before_dataset_search(params)

        assert result is params
        assert result == {
            "q": "",
            "fq": ['organization:"sfb1153"'],
            "sort": "metadata_modified desc",
        }


def test_valid_special_search_is_preserved_before_solr():
    from ckanext.crc1153.plugins.crc_search import CrcSearchPlugin

    params = {"q": "column:force", "fq": ['tags:"experiment"']}

    result = CrcSearchPlugin().before_dataset_search(params)

    assert result is params
    assert result == {"q": "column:force", "fq": ['tags:"experiment"']}


def test_non_special_empty_field_query_is_preserved():
    from ckanext.crc1153.plugins.crc_search import CrcSearchPlugin

    params = {"q": "title:", "fq": [""]}

    result = CrcSearchPlugin().before_dataset_search(params)

    assert result["q"] == "title:"


def test_missing_or_non_string_query_is_preserved():
    from ckanext.crc1153.plugins.crc_search import CrcSearchPlugin

    for query in (None, 42):
        params = {"q": query, "fq": [""]}

        result = CrcSearchPlugin().before_dataset_search(params)

        assert result is params
        assert result["q"] == query
