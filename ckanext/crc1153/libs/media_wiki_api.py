from mwclient import Site


class API():
    
    username = None
    password = None
    site = None
    host = ""
    path = "/wiki/"
    scheme = "https"
    query = ""    
    image_field = ""


    def __init__(self, username, password, query, host, sample_query=False):
        self.username = username
        self.password = password
        self.query = query
        self.host = host
        self.sample_query = sample_query        
        self.image_field = "Image"
    

    def pipeline(self):
        results = []        
        self.login(self.host, self.path, self.scheme)
        try:            
            self.login(self.host, self.path, self.scheme)
            raw_results = self.site.ask(self.query)                            
            for answer in raw_results:
               results.append(answer['fulltext'])
        except:
            return []
            
        return []


    def login(self, host: str, path: str, scheme: str):
        site_ = Site(host=host, path=path, scheme=scheme)
        if self.username and self.password:
            site_.login(username=self.username, password=self.password)        
        self.site = site_
        return True
    