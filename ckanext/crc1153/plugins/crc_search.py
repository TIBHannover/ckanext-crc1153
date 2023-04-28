import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_search.data_column_helpers import ColumnSearch
from ckanext.crc1153.libs.crc_search.sample_search_helpers import SampleSearch
from ckanext.crc1153.libs.crc_search.publication_search_helpers import PublicationSearch
from ckanext.crc1153.libs.crc_search.extra_metadata_helpers import ExtraMetadataSearch
from ckanext.crc1153.libs.crc_search.file_helpers import FileHelper
from ckanext.crc1153.libs.crc_search.indexer_helper import IndexerHelper
from ckanext.crc1153.libs.commons import Commons
from ckanext.crc1153.models.data_resource_column_index import DataResourceColumnIndex
from flask import Blueprint



class CrcSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IBlueprint)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates/crc_search')
        

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)        
        blueprint.add_url_rule(
            u'/crc_search/indexer',
            u'indexer',
            IndexerHelper.indexer,
            methods=['GET']
            )           

        return blueprint 
    

    # IPackageController

    def after_search(self, search_results, search_params):
        try:
            search_types = ['column', 'publication', 'sample', 'material_combination', 'demonstrator', 'manufacturing_process', 'analysis_method']
            search_query = search_params['q'].lower()
            if search_query.split(':')[0].lower() not in search_types:
                return search_results
            
            elif len(search_query.split('column:')) > 1:         
                search_results = ColumnSearch.run(search_query=search_query, search_params=search_params, search_results=search_results)
            
            elif len(search_query.split('publication:')) > 1 and Commons.check_plugin_enabled("dataset_reference"):
                search_results = PublicationSearch.run(search_query=search_query, search_params=search_params, search_results=search_results)
                        
            elif len(search_query.split('sample:')) > 1 and Commons.check_plugin_enabled("sample_link"):     
                search_results = SampleSearch.run(search_query=search_query, search_params=search_params, search_results=search_results)
            
            elif len(search_query.split('material_combination:')) > 1 and Commons.check_plugin_enabled("crc1153_specific_metadata"):
                target_metadata = 'material_combination'
                search_results = ExtraMetadataSearch.run(search_query=search_query, search_params=search_params, target_metadata_name=target_metadata, search_results=search_results)
            
            elif len(search_query.split('demonstrator:')) > 1 and Commons.check_plugin_enabled("crc1153_specific_metadata"):                
                target_metadata = 'demonstrator'
                search_results = ExtraMetadataSearch.run(search_query=search_query, search_params=search_params, target_metadata_name=target_metadata, search_results=search_results)
            
            elif len(search_query.split('manufacturing_process:')) > 1 and Commons.check_plugin_enabled("crc1153_specific_metadata"):
                target_metadata = 'manufacturing_process'
                search_results = ExtraMetadataSearch.run(search_query=search_query, search_params=search_params, target_metadata_name=target_metadata, search_results=search_results)
                            
            elif len(search_query.split('analysis_method:')) > 1 and Commons.check_plugin_enabled("crc1153_specific_metadata"):          
                target_metadata = 'analysis_method'
                search_results = ExtraMetadataSearch.run(search_query=search_query, search_params=search_params, target_metadata_name=target_metadata, search_results=search_results)

            else:
                return search_results

            return search_results
        
        except:
            # return search_results
            raise
  

    def after_delete(self, context, pkg_dict):
        dataset = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
        for resource in dataset['resources']:
            column_indexer = DataResourceColumnIndex()
            records = column_indexer.get_by_resource(id=resource['id'])
            for rec in records:
                rec.delete()
                rec.commit()

        return pkg_dict

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_create(self, context, pkg_dict):
        return pkg_dict

    def after_update(self, context, pkg_dict):
        return pkg_dict

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
        if "url_type" not in resource.keys():
            return resource

        if resource['url_type'] == 'upload':
            if FileHelper.is_csv(resource):
                dataframe_columns, _ = FileHelper.get_csv_columns(resource['id'])
                columns_names = ""
                for col in dataframe_columns:
                    columns_names += (col + ",")
                column_indexer = DataResourceColumnIndex(resource_id=resource['id'], columns_names=columns_names)
                column_indexer.save()
            
            elif FileHelper.is_xlsx(resource):
                xls_dataframes_columns = FileHelper.get_xlsx_columns(resource['id'])
                columns_names = ""
                for sheet, columns_object in xls_dataframes_columns.items():
                    for col in columns_object[0]:  
                        columns_names += (col + ",")
                
                column_indexer = DataResourceColumnIndex(resource_id=resource['id'], columns_names=columns_names)
                column_indexer.save()
  
        return resource



    def before_delete(self, context, resource, resources):
        if not FileHelper.is_csv(resource) and not FileHelper.is_xlsx(resource):
            return resource
        column_indexer = DataResourceColumnIndex()
        records = column_indexer.get_by_resource(id=resource['id'])
        for rec in records:
            rec.delete()
            rec.commit()
        return resources    

    
    def after_delete(self, context, resources):        
        return resources

    def before_create(self, context, resource):
        return resource

    def before_update(self, context, current, resource):
        return resource
    
    def after_update(self, context, resource):
        return resource    
    
    def before_show(self, resource_dict):
        return resource_dict