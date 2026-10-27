import logging

import ckan.plugins.toolkit as toolkit
from mwclient import Site, errors
from requests import exceptions as requests_exceptions

from ckanext.crc1153.libs.auth_helpers import AuthHelpers


log = logging.getLogger(__name__)


DEFAULT_MEDIAWIKI_SCHEME = "https"
DEFAULT_MEDIAWIKI_HOST = "smw.service.tib.eu"
DEFAULT_MEDIAWIKI_PATH = "/wiki-sfb1153/"
DEFAULT_MEDIAWIKI_TIMEOUT = 30
SMW_MEDIAWIKI_HOST = "ckanext.smw.mediawiki.api.endpoint"
SMW_MEDIAWIKI_PATH = "ckanext.smw.mediawiki.api.path"
SMW_MEDIAWIKI_SCHEME = "ckanext.smw.mediawiki.api.scheme"


class MediaWikiAPI():

    def __init__(self, query, query_type="", sample_query=False):
        creds = AuthHelpers.get_mediaWiki_creds()
        self.username = creds.get('username')
        self.password = creds.get('password')
        self.query = query
        project_id = str(toolkit.config.get("ckanext.crc.project.id", "")).strip()
        if project_id == "1368":
            default_path = "/wiki-sfb1368/"
            self.host = toolkit.config.get(SMW_MEDIAWIKI_HOST, DEFAULT_MEDIAWIKI_HOST)
            self.path = toolkit.config.get(SMW_MEDIAWIKI_PATH, default_path)
            self.scheme = toolkit.config.get(
                SMW_MEDIAWIKI_SCHEME, DEFAULT_MEDIAWIKI_SCHEME
            )
        else:
            self.host = toolkit.config.get(
                "ckanext.crc1153.mediawiki.host", DEFAULT_MEDIAWIKI_HOST
            )
            self.path = toolkit.config.get(
                "ckanext.crc1153.mediawiki.path", DEFAULT_MEDIAWIKI_PATH
            )
            self.scheme = toolkit.config.get(
                "ckanext.crc1153.mediawiki.scheme", DEFAULT_MEDIAWIKI_SCHEME
            )
        self.sample_query = sample_query
        self.image_field = "Image"
        self.site = None
        self.timeout = self._configured_timeout()
        self.query_type = query_type


    def pipeline(self):
        results = []
        try:
            self.login(self.host, self.path, self.scheme)
            raw_results = self.site.ask(self.query)
            for answer in raw_results:
               results.append(self.process_answer(self.query_type, answer))
            return results
        except (
            errors.MwClientError,
            requests_exceptions.RequestException,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as err:
            log.warning(
                "MediaWiki query failed for %s://%s%s: %s",
                self.scheme,
                self.host,
                self.path,
                err.__class__.__name__,
            )
            return []


    def login(self, host: str, path: str, scheme: str):
        site_ = Site(
            host=host,
            path=path,
            scheme=scheme,
            reqs={"timeout": self.timeout},
        )
        if self.username and self.password:
            site_.login(username=self.username, password=self.password)
        self.site = site_
        return True

    def _configured_timeout(self):
        configured_timeout = toolkit.config.get(
            "ckanext.crc1153.mediawiki.timeout", DEFAULT_MEDIAWIKI_TIMEOUT
        )
        try:
            return int(configured_timeout)
        except (TypeError, ValueError):
            log.warning(
                "Invalid MediaWiki timeout configured, using default %s seconds",
                DEFAULT_MEDIAWIKI_TIMEOUT,
            )
            return DEFAULT_MEDIAWIKI_TIMEOUT


    def process_answer(self, query_type, record):
        if query_type == "material":
            return record['fulltext']
        printouts = record['printouts']
        values = printouts.get('RepresentsDemonstrator', printouts.get('Demonstrator'))
        value = values[0]
        if isinstance(value, dict):
            return value.get('fulltext') or value.get('text')
        return value


