# encoding: utf-8

import ckan.plugins.toolkit as toolkit


class CrcSpecificMetadataHelpers:


    @staticmethod
    def updateResourceSchema(schema):        
        schema['resources'].update({'material_combination' : [toolkit.get_validator('ignore_missing')] })
        schema['resources'].update({'demonstrator' : [toolkit.get_validator('ignore_missing')] })
        schema['resources'].update({'manufacturing_process' : [toolkit.get_validator('ignore_missing')] })        
        schema['resources'].update({'analysis_method' : [toolkit.get_validator('ignore_missing')] })
        schema['resources'].update({'is_automated_processed' : [toolkit.get_validator('ignore_missing')] })
        return schema