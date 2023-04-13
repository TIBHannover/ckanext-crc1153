# encoding: utf-8

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.crc1153.libs.crc_specific_metadata.helpers import CrcSpecificMetadataHelpers
from ckanext.crc1153.controllers.crcSpecificMetadataController import CrcSpecificMetadataController



class CrcSpecificMetadata(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IDatasetForm, inherit=False)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, '../templates')
        toolkit.add_public_directory(config_, '../public')
        toolkit.add_resource('../public/crc_specific_metadata', 'ckanext-crc1153-specific-metadata')
    

    # Blueprint

    def get_blueprint(self):

        blueprint = Blueprint(self.name, self.__module__)        
        blueprint.add_url_rule(
            u'/resource_custom_metadata/add_metadata/<package_id>',
            u'add_metadata',
            CrcSpecificMetadataController.render_add_metadata_page,
            methods=['GET']
            )
        blueprint.add_url_rule(
            u'/resource_custom_metadata/save_metadata',
            u'save_metadata',
            CrcSpecificMetadataController.save_metadata,
            methods=['POST']
            )                   
        return blueprint
    
    
    # IDatasetForm
    
    def is_fallback(self):
        return True

    def package_types(self):
        return []

    def create_package_schema(self):
        schema = super(CrcSpecificMetadata, self).create_package_schema()
        schema = CrcSpecificMetadataHelpers.updateResourceSchema(schema)
        return schema

    def update_package_schema(self):
        schema = super(CrcSpecificMetadata, self).update_package_schema()
        schema = CrcSpecificMetadataHelpers.updateResourceSchema(schema)
        return schema

    def show_package_schema(self):
        schema = super(CrcSpecificMetadata, self).show_package_schema()
        schema = CrcSpecificMetadataHelpers.updateResourceSchema(schema)
        return schema
    