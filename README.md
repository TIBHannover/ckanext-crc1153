
# ckanext-crc1153

This is the CKAN extension for the project CRC (SFB) 1153. The extensions includes the plugins that are implemented specifically for CRC1153. 


TODO:

- Move get_json from crc_layout to dcat profile plugin




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

To use the plugins that needs Semantic Media Wiki APIs, the credentials need to be in a text file with this format:

     username=YYY
     password=XXXX 

The credentials file path need to be set in the **ckan.ini** file with the name:

     ckanext.mediaWiki_credentials_path = /YOUR_Credential_PATH/




## Tests

TBA



## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
