from ckanext.crc1153.libs import auth_helpers
from ckanext.crc1153.libs.auth_helpers import AuthHelpers
from ckan.common import CKANConfig
from ckan.config.declaration import Declaration, Key
from ckanext.crc1153.plugins.crc_profile import Dcatapcrc1153Plugin


CANONICAL_CREDENTIALS_KEY = "ckanext.crc1153.mediawiki_credentials_path"
SHARED_CREDENTIALS_KEY = "ckanext.mediawiki_credentials_path"
HISTORICAL_CREDENTIALS_KEY = "ckanext.mediaWiki_credentials_path"


def _credentials_file(tmp_path, name, username):
    credentials = tmp_path / name
    credentials.write_text(
        "username={}\npassword=test-password\n".format(username)
    )
    return str(credentials)


def _declared_config(values):
    declaration = Declaration()
    Dcatapcrc1153Plugin().declare_config_options(declaration, Key())
    config = CKANConfig(values)
    declaration.make_safe(config)
    return config


def test_crc_owned_mediawiki_credentials_work_without_smw(monkeypatch, tmp_path):
    monkeypatch.setattr(
        auth_helpers.toolkit,
        "config",
        {
            CANONICAL_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "canonical.credentials", "canonical-user"
            )
        },
    )

    assert AuthHelpers.get_mediaWiki_creds() == {
        "username": "canonical-user",
        "password": "test-password",
    }


def test_shared_mediawiki_credentials_remain_supported(monkeypatch, tmp_path):
    monkeypatch.setattr(
        auth_helpers.toolkit,
        "config",
        {
            SHARED_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "shared.credentials", "shared-user"
            )
        },
    )

    assert AuthHelpers.get_mediaWiki_creds()["username"] == "shared-user"


def test_historical_mediawiki_credentials_remain_supported(monkeypatch, tmp_path):
    config = _declared_config(
        {
            HISTORICAL_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "historical.credentials", "historical-user"
            )
        }
    )
    monkeypatch.setattr(auth_helpers.toolkit, "config", config)

    assert AuthHelpers.get_mediaWiki_creds()["username"] == "historical-user"


def test_crc_owned_credentials_take_precedence(monkeypatch, tmp_path):
    monkeypatch.setattr(
        auth_helpers.toolkit,
        "config",
        {
            CANONICAL_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "canonical.credentials", "canonical-user"
            ),
            SHARED_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "shared.credentials", "shared-user"
            ),
            HISTORICAL_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "historical.credentials", "historical-user"
            ),
        },
    )

    assert AuthHelpers.get_mediaWiki_creds()["username"] == "canonical-user"


def test_shared_credentials_take_precedence_over_historical(monkeypatch, tmp_path):
    config = _declared_config(
        {
            SHARED_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "shared.credentials", "shared-user"
            ),
            HISTORICAL_CREDENTIALS_KEY: _credentials_file(
                tmp_path, "historical.credentials", "historical-user"
            ),
        }
    )
    monkeypatch.setattr(auth_helpers.toolkit, "config", config)

    assert AuthHelpers.get_mediaWiki_creds()["username"] == "shared-user"


def test_missing_mediawiki_credentials_path_remains_optional(monkeypatch):
    monkeypatch.setattr(auth_helpers.toolkit, "config", {})

    assert AuthHelpers.get_mediaWiki_creds() == {}
