# encoding: utf-8

import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
from ckanext.crc1153.libs.auth_helpers import AuthHelpers


class Helper():
    

    @staticmethod
    def stages_count():
        plugins_with_stages = ['crc1153_specific_metadata', 'organization_group', 'machine_link', 'sample_link']
        enabled_plugins = toolkit.config.get("ckan.plugins")
        count = 0
        for pl in plugins_with_stages:
            if pl in enabled_plugins:
                count += 1
        
        return count


    @staticmethod
    def set_active_stage():
        stages= []                  
        if  'dataset/new' in  h.full_current_url():
            stages = ['active', 'uncomplete','uncomplete', 'uncomplete', 'uncomplete', 'uncomplete']
        
        elif 'resource/new' in h.full_current_url():
            stages = ['complete', 'active','uncomplete', 'uncomplete', 'uncomplete', 'uncomplete']
                    
        elif 'upgrade_dataset/add_ownership_view' in h.full_current_url():
            stages = ['complete', 'complete','active', 'uncomplete', 'uncomplete', 'uncomplete']
        
        elif 'resource_custom_metadata/add_metadata' in h.full_current_url():
            stages = ['complete', 'complete','complete', 'active', 'uncomplete', 'uncomplete']
        
        elif 'smw/machines_view' in h.full_current_url():
            stages = ['complete', 'complete','complete', 'complete', 'active', 'uncomplete']
        
        elif '/smw/add_samples_view' in h.full_current_url():
            stages = ['complete', 'complete','complete', 'complete', 'complete', 'active']
        
        return stages


    @staticmethod
    def set_stage_orders():
        return ['second', 'third', 'forth', 'fifth']
    


    @staticmethod
    def set_stage_titles():
        return ['Add data', 'Ownership', 'Extra Metadata', 'Equipment(s)', 'Sample(s)'] 



    @staticmethod
    def search_query_prepration(query):
        if "sample:" in query:
            return [query.split(":")[1], "sample"]
        elif "column:" in query:
            return [query.split(":")[1], "column"]        
        elif "publication:" in query:
            return [query.split(":")[1], "publication"]
        elif "material_combination:" in query:
            return [query.split(":")[1], "material_combination"]
        elif "demonstrator:" in query:
            return [query.split(":")[1], "demonstrator"]
        elif "manufacturing_process:" in query:
            return [query.split(":")[1], "manufacturing_process"]
        elif "analysis_method:" in query:
            return [query.split(":")[1], "analysis_method"]
        else:
            return [query, '0']
    


    @staticmethod
    def search_type_selection_is_needed(form_id):
        if form_id in ["organization-search-form", "group-search-form"]:
            return False
        return True
    

    @staticmethod
    def get_dataset_export_url(dataset_name, format):        
        base_url = toolkit.config.get('ckan.site_url')
        path = toolkit.config.get('ckan.root_path')                      
        if path:
            path = path.split("{{LANG}}")[0]
            return base_url + path + 'dataset/' + dataset_name + format
        return base_url + '/dataset/' + dataset_name + format


   
    def get_json(dataset_name):
        package = toolkit.get_action('package_show')({}, {'name_or_id': dataset_name})
        if not AuthHelpers.check_access_show_package(package['id']):
                return toolkit.abort(403, "Not Authorized")
       
        return package
       

    
    