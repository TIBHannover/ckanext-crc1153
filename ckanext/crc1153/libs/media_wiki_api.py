from mwclient import Site
from ckanext.crc1153.libs.auth_helpers import AuthHelpers


class MediaWikiAPI():
                 
    def __init__(self, query, query_type="", sample_query=False):
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
        self.query_type = query_type
    

    def pipeline(self):
        results = []                
        try:
            self.login(self.host, self.path, self.scheme)            
            raw_results = self.site.ask(self.query)                            
            for answer in raw_results:
               results.append(self.process_answer(self.query_type, answer))
            return results
        except:
            return []
                    

    def login(self, host: str, path: str, scheme: str):
        site_ = Site(host=host, path=path, scheme=scheme)
        if self.username and self.password:
            site_.login(username=self.username, password=self.password)        
        self.site = site_
        return True
    

    def process_answer(self, query_type, record):
        if query_type == "material":
            return record['fulltext']
        return record['printouts']['Demonstrator'][0]
    
    