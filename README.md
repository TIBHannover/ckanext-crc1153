
# ckanext-crc1153

This is the CKAN extension for the project CRC (SFB) 1153. The extensions includes the plugins that are implemented specifically for CRC1153. 


## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8 and earlier | not tested    |
| 2.9             | Yes    |


## Plugins

- **crc1153_layout**
- **crc1153_specific_metadata**
- **crc1153_system_stats**
- **crc1153_dcat_ap**
- **crc1153_search**


## Installation


To install ckanext-crc1153:

1. Activate your CKAN virtual environment, for example:

          . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

          git clone git@github.com:TIBHannover/ckanext-crc1153.git
          cd ckanext-crc1153
          pip install -e .
          pip install -r requirements.txt

3. Add the needed plugin name(s) to **ckan.ini** (plugin names are mentioned in the last section)

4. (For some plugins) if the plugin has migration, ckan migration is needed. Look at: https://docs.ckan.org/en/2.9/extensions/best-practices.html#use-migrations-when-introducing-new-models


5. Restart CKAN and the web server. 

          sudo service supervisor reload
          sudo service nginx reload


## Config settings

1. To use the plugins that needs Semantic Media Wiki APIs, the credentials need to be in a text file with this format:

     username=YYY
     password=XXXX 

The credentials file path need to be set in the **ckan.ini** file with the name:

     ckanext.mediaWiki_credentials_path = /YOUR_Credential_PATH/

2. To use the plugins that needs Apache Jena Endpoint (such as crc1153_dcat_ap), you need to set the endpoint in **ckan.ini**

          ckanext.apacheJena.endpoint = APACHE_JENA_ENDPOINT/update

3. The **crc1153_search** has a feature to search for data resources that are in CSV/XLSX formats based on their columns' name. The search works based on an indexing table to boost the search speed. The indexer auotomatically index a new resource. However, to index the already existing data resources, you need to call the indexer endpoint (Only Admin can run this):

          GET   "CKAN_BASE_URL/crc_search/indexer"


## Tests

TBA



## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
