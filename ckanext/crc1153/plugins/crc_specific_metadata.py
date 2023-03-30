# encoding: utf-8

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_specific_metadata.helpers import CrcSpecificMetadataHelpers



class CrcSpecificMetadata(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm, inherit=False)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates/crc_specific_metadata')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/crc_specific_metadata', 'ckanext-crc1153-specific-metadata')
    

    
    # IDatasetForm
    
    def is_fallback(self):
        return True

    def package_types(self):
        return []

    def create_package_schema(self):
        schema = super(ResourceCustomMetadataPlugin, self).create_package_schema()
        schema = CrcSpecificMetadataHelpers.updateResourceSchema(schema)
        return schema

    def update_package_schema(self):
        schema = super(ResourceCustomMetadataPlugin, self).update_package_schema()
        schema = CrcSpecificMetadataHelpers.updateResourceSchema(schema)
        return schema

    def show_package_schema(self):
        schema = super(ResourceCustomMetadataPlugin, self).show_package_schema()
        schema = CrcSpecificMetadataHelpers.updateResourceSchema(schema)
        return schema
    