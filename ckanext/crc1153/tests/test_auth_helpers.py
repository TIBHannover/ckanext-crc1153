from ckanext.crc1153.libs import auth_helpers
from ckanext.crc1153.libs.auth_helpers import AuthHelpers


CANONICAL_CREDENTIALS_KEY = "ckanext.mediawiki_credentials_path"


def test_mediawiki_credentials_use_canonical_config_key(monkeypatch, tmp_path):
    credentials = tmp_path / "mediawiki.credentials"
    credentials.write_text("username=test-user\npassword=test-password\n")
    monkeypatch.setattr(
        auth_helpers.toolkit,
        "config",
        {CANONICAL_CREDENTIALS_KEY: str(credentials)},
    )

    assert AuthHelpers.get_mediaWiki_creds() == {
        "username": "test-user",
        "password": "test-password",
    }


def test_missing_mediawiki_credentials_path_remains_optional(monkeypatch):
    monkeypatch.setattr(auth_helpers.toolkit, "config", {})

    assert AuthHelpers.get_mediaWiki_creds() == {}
