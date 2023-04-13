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
        api_call = MediaWikiAPI(query=query, query_type="material")
        matarials = [{"value": "0", "text": "None selected"}]
        for material_name in api_call.pipeline():
            temp = {}
            temp['value'] = material_name
            temp['text'] = material_name
            matarials.append(temp)
        return matarials


    @staticmethod
    def get_demonstrator_list():        
        query = "[[Category:Samples]] [[RepresentsDemonstrator::+]]|?RepresentsDemonstrator"
        api_call = MediaWikiAPI(query=query, query_type="demontrator")
        demonstrators = [{"value": "0", "text": "None selected"}]
        api_result = set(api_call.pipeline())
        for demons_name in api_result:            
            temp = {}
            temp['value'] = demons_name
            temp['text'] = demons_name
            demonstrators.append(temp)
        return demonstrators