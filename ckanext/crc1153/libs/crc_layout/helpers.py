# encoding: utf-8

import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h



class Helper():
    
    @staticmethod
    def which_sfb():
        '''
            Check which sfb server the plugin is runnung in. 
        '''

        ckan_root_path = toolkit.config.get('ckan.root_path')
        if  ckan_root_path and 'sfb1368/ckan' in ckan_root_path:
            return '1368'
        elif ckan_root_path and 'sfb1153/ckan' in ckan_root_path:
            return '1153'
        else:
            # localhost
            return '1153'
    

    @staticmethod
    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins")
        if plugin_name in plugins:
            return True
        return False
    

    @staticmethod
    def stages_count():
        plugins_with_stages = ['resource_custom_metadata', 'organization_group', 'semantic_media_wiki', 'sample_link']
        enabled_plugins = toolkit.config.get("ckan.plugins")
        count = 0
        for pl in plugins_with_stages:
            if pl in enabled_plugins:
                count += 1
        
        return count


    @staticmethod
    def set_stages():
        stages= []
        if Helper.which_sfb() == '1368':
            if  'dataset/new' in  h.full_current_url():
                stages = ['active', 'uncomplete','uncomplete', 'uncomplete', 'uncomplete']
            
            elif 'resource/new' in h.full_current_url():
                stages = ['complete', 'active','uncomplete', 'uncomplete', 'uncomplete']
            
            elif 'resource_custom_metadata/index' in h.full_current_url():
                stages = ['complete', 'complete','active', 'uncomplete', 'uncomplete']
            
            elif 'upgrade_dataset/add_ownership_view' in h.full_current_url():
                stages = ['complete', 'complete','complete', 'active', 'uncomplete']
            
            elif 'smw/machines_view' in h.full_current_url():
                stages = ['complete', 'complete','complete', 'complete', 'active']
        
        else:
            # 1153
            if  'dataset/new' in  h.full_current_url():
                stages = ['active', 'uncomplete','uncomplete', 'uncomplete', 'uncomplete']
            
            elif 'resource/new' in h.full_current_url():
                stages = ['complete', 'active','uncomplete', 'uncomplete', 'uncomplete']
                        
            elif 'upgrade_dataset/add_ownership_view' in h.full_current_url():
                stages = ['complete', 'complete','active', 'uncomplete', 'uncomplete']
            
            elif 'smw/machines_view' in h.full_current_url():
                stages = ['complete', 'complete','complete', 'active', 'uncomplete']
            
            elif '/smw/add_samples_view' in h.full_current_url():
                stages = ['complete', 'complete','complete', 'complete', 'active']
        
        return stages


    @staticmethod
    def set_orders():
        if Helper.which_sfb() == '1368':
            return ['second', 'third', 'forth']
        else:
            return ['second', 'third', 'forth']
    


    @staticmethod
    def set_titles():
        if Helper.which_sfb() == '1368':
            return ['Add data', 'Metadata', 'Ownership', 'Equipment(s)'] 
        else:
            return ['Add data', 'Ownership', 'Equipment(s)', 'Sample(s)'] 



    @staticmethod
    def search_query_prepration(query):
        if "sample:" in query:
            return [query.split(":")[1], "sample"]
        elif "column:" in query:
            return [query.split(":")[1], "column"]
        elif "material_combination:" in query:
            return [query.split(":")[1], "material_combination"]
        elif "surface_preparation:" in query:
            return [query.split(":")[1], "surface_preparation"]
        elif "atmosphere:" in query:
            return [query.split(":")[1], "atmosphere"]
        elif "data_type:" in query:
            return [query.split(":")[1], "data_type"]
        elif "analysis_method:" in query:
            return [query.split(":")[1], "analysis_method"]
        elif "publication:" in query:
            return [query.split(":")[1], "publication"]
        else:
            return [query, '0']
    


    @staticmethod
    def is_selection_needed(form_id):
        if form_id in ["organization-search-form", "group-search-form"]:
            return False
        return True
    

    @staticmethod
    def get_export_url(dataset_name, format):        
        base_url = toolkit.config.get('ckan.site_url')
        path = toolkit.config.get('ckan.root_path')                      
        if path:
            path = path.split("{{LANG}}")[0]
            return base_url + path + 'dataset/' + dataset_name + format
        return base_url + '/dataset/' + dataset_name + format


   
    def get_json(dataset_name):
        package = toolkit.get_action('package_show')({}, {'name_or_id': dataset_name})
        if not Helper.check_access_show_package(package['id']):
                return toolkit.abort(403, "Not Authorized")
       
        return package
       

    def check_access_show_package(package_id):
        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        data_dict = {'id':package_id}
        try:
            toolkit.check_access('package_show', context, data_dict)
            return True

        except toolkit.NotAuthorized:
            return False
    