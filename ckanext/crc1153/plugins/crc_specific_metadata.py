# encoding: utf-8

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

class CrcSpecificMetadata(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates/crc_specific_metadata')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/crc_specific_metadata', 'ckanext-crc1153-specific-metadata')
    
    
    
    