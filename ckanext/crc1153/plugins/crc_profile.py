import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckanext.crc1153.controllers.crcDcatProfileController import Crc1153DcatProfileController
from ckanext.crc1153.libs.crc_profile.helpers import Crc1153DcatProfileHelper as Helper


class Dcatapcrc1153Plugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics', 'ckanext-dcatapcrc')


    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__) 
        blueprint.add_url_rule(
            u'/dcatapcrc/load_admin_view',
            u'load_admin_view',
            Crc1153DcatProfileController.load_admin_view,
            methods=['GET']
            )   
        
        blueprint.add_url_rule(
            u'/dcatapcrc/export_catalog',
            u'export_catalog',
            Crc1153DcatProfileController.export_catalog,
            methods=['GET']
            )   
        
        return blueprint 
    

    # IPackageController

    
    def after_create(self, context, pkg_dict):
        '''
            Post the dataset metadata to the sparql endpoint
        '''

        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
            graph = Helper.get_dataset_graph(package)
            res = Helper.insert_to_sparql(graph)
        except:
            return pkg_dict
            # raise

        return pkg_dict

    

    def after_update(self, context, pkg_dict):
        '''
            Upadte an existing dataset metadata on the sparql endpoint
        '''

        try:            
            package = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})            
            graph = Helper.get_dataset_graph(package)
            res_d = Helper.delete_from_sparql(graph)
            res_i = Helper.insert_to_sparql(graph)
        except:
            return pkg_dict
            # raise
                               
        return pkg_dict
    
    

    def after_delete(self, context, pkg_dict):
        '''
            Delete an existing dataset metadata on the sparql endpoint
        '''

        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
            graph = Helper.get_dataset_graph(package)
            res_d = Helper.delete_from_sparql(graph)            
        except:
            return pkg_dict
            # raise
        
        return pkg_dict
    


    def after_search(self, search_results, search_params):        
        return search_results
    
    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_show(self, context, pkg_dict):
        return pkg_dict

    def before_search(self, search_params):
        return search_params

    def before_index(self, pkg_dict):
        return pkg_dict

    def before_view(self, pkg_dict):
        return pkg_dict
    


     # IResourceController

    def after_create(self, context, resource):        
        return resource
    
    def after_update(self, context, resource):
        try:
            package = {}
            if resource.get("package_id"):   
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource['package_id']})
            elif resource.get('name'):
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource['name']})
            graph = Helper.get_dataset_graph(package)
            res_d = Helper.delete_from_sparql(graph)
            res_i = Helper.insert_to_sparql(graph)
        except:
            return resource
            # raise
        
        return resource
    

    
    def before_delete(self, context, resource, resources):
        try:
            package = {}
            resource_dict = toolkit.get_action('resource_show')({}, {'id': resource['id']}) 
            if resource_dict.get("package_id"):   
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource_dict['package_id']})
            elif resource_dict.get('name'):
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource_dict['name']})

            graph = Helper.get_dataset_graph(package)
            res_d = Helper.delete_from_sparql(graph)            
        except:
            return resource
            # raise                 
        return resources
    
    
    
    def after_delete(self, context, resources):        
        return resources


    def before_create(self, context, resource):
        return resource

    def before_update(self, context, current, resource):
        return resource
     
    def after_delete(self, context, resources):
        return resources
    
    def before_show(self, resource_dict):
        return resource_dict
    

