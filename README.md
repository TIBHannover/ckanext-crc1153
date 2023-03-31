
# ckanext-crc1153

This is the CKAN extension for the project CRC (SFB) 1153. The extensions includes all the plugins used in the project. 


TODO:

- Move get_json from crc_layout to dcat profile plugin
- Move the common function among all plugins to a common library
- Remove the duplicated template helpers function after adding all plugins




## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.8 and earlier | not tested    |
| 2.9             | Yes    |



## Installation


To install ckanext-crc1153:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-crc1153.git
    cd ckanext-crc1153
    pip install -e .
	pip install -r requirements.txt


4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

None at present




## Tests

TBA



## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
