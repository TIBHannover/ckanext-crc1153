# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.media_wiki_api import MediaWikiAPI


class CrcSpecificMetadataHelpers:


    @staticmethod
    def updateResourceSchema(schema):        
        schema['resources'].update({'material_combination' : [toolkit.get_validator('ignore_missing')] })
        schema['resources'].update({'demonstrator' : [toolkit.get_validator('ignore_missing')] })
        schema['resources'].update({'manufacturing_process' : [toolkit.get_validator('ignore_missing')] })        
        schema['resources'].update({'analysis_method' : [toolkit.get_validator('ignore_missing')] })
        schema['resources'].update({'is_automated_processed' : [toolkit.get_validator('ignore_missing')] })
        return schema


    @staticmethod
    def get_material_list():        
        query = "[[Category:SampleMaterial]]"
        api_call = MediaWikiAPI(query=query)
        matarials = []
        for material_name in api_call.pipeline():
            temp = {}
            temp['value'] = material_name
            temp['text'] = material_name
            matarials.append(temp)
        return matarials