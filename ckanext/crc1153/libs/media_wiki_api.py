from mwclient import Site
from ckanext.crc1153.libs.auth_helpers import AuthHelpers


class MediaWikiAPI():
                 
    def __init__(self, query, sample_query=False):
        creds = AuthHelpers.get_mediaWiki_creds()
        self.username = creds['username']
        self.password = creds['password']
        self.query = query
        self.host = "service.tib.eu/sfb1153"
        self.sample_query = sample_query        
        self.image_field = "Image"
        self.site = None
        self.path = "/wiki/"
        self.scheme = "https"
    

    def pipeline(self):
        results = []        
        self.login(self.host, self.path, self.scheme)
        try:            
            self.login(self.host, self.path, self.scheme)
            raw_results = self.site.ask(self.query)                            
            for answer in raw_results:
               results.append(answer['fulltext'])
            return results
        except:
            return []
            
        return []


    def login(self, host: str, path: str, scheme: str):
        site_ = Site(host=host, path=path, scheme=scheme)
        if self.username and self.password:
            site_.login(username=self.username, password=self.password)        
        self.site = site_
        return True
    