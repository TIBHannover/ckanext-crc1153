import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.model import Package
from ckanext.crc1153.libs.crc_search.data_column_helpers import ColumnSearchHelper
from ckanext.crc1153.libs.crc_search.sample_search_helpers import SampleSearchHelper
from ckanext.crc1153.libs.crc_search.publication_search_helpers import PublicationSearchHelper
from ckanext.crc1153.libs.crc_search.extra_metadata_helpers import ExtraMetadataSearchHelper
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
# from ckanext.sfb_search_extension.models.data_resource_column_index import DataResourceColumnIndex
from flask import Blueprint



class CrcSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IBlueprint)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, '../templates')
        

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)        
        blueprint.add_url_rule(
            u'/sfb_search/indexer',
            u'indexer',
            SearchHelper.indexer,
            methods=['GET']
            )   
        

        return blueprint 
    

    # IPackageController

    def after_search(self, search_results, search_params):        
        search_mode = ''
        target_metadata = ""
        search_types = ['column', 'sample', 'material_combination', 'surface_preparation', 'atmosphere', 'data_type', 'analysis_method', 'publication']
        if search_params['q'].split(':')[0].lower() not in search_types:
            return search_results
        
        elif len(search_params['q'].lower().split('column:')) > 1:            
            search_phrase = search_params['q'].lower().split('column:')[1].strip().lower()
            search_mode = 'column'
        
        elif len(search_params['q'].lower().split('publication:')) > 1:            
            search_phrase = search_params['q'].lower().split('publication:')[1].strip().lower()
            search_mode = 'publication'
        
        elif len(search_params['q'].lower().split('sample:')) > 1:
            search_phrase = search_params['q'].lower().split('sample:')[1].strip().lower()
            search_mode = 'sample'
        
        elif len(search_params['q'].lower().split('material_combination:')) > 1:
            search_phrase = search_params['q'].lower().split('material_combination:')[1].strip().lower()
            target_metadata = 'material_combination'
            search_mode = "resource_metadata"
        
        elif len(search_params['q'].lower().split('surface_preparation:')) > 1:
            search_phrase = search_params['q'].lower().split('surface_preparation:')[1].strip().lower()
            target_metadata = 'surface_preparation'
            search_mode = "resource_metadata"
        
        elif len(search_params['q'].lower().split('atmosphere:')) > 1:
            search_phrase = search_params['q'].lower().split('atmosphere:')[1].strip().lower()
            target_metadata = 'atmosphere'
            search_mode = "resource_metadata"
        
        elif len(search_params['q'].lower().split('data_type:')) > 1:
            search_phrase = search_params['q'].lower().split('data_type:')[1].strip().lower()
            target_metadata = 'data_type'
            search_mode = "resource_metadata"
        
        elif len(search_params['q'].lower().split('analysis_method:')) > 1:
            search_phrase = search_params['q'].lower().split('analysis_method:')[1].strip().lower()
            target_metadata = 'analysis_method'
            search_mode = "resource_metadata"

        else:            
            return search_results

        # empty the search result to remove unrelated search result by ckan.
        search_results['results'] = []
        search_results['search_facets']['organization']['items'] = []
        search_results['search_facets']['tags']['items'] = []
        search_results['search_facets']['groups']['items'] = []
        if(search_results['search_facets'].get('sfb_dataset_type')):
            search_results['search_facets']['sfb_dataset_type']['items'] = []
        search_results['count'] = 0
        search_results['detected_resources_ids'] = []
        search_filters = search_params['fq'][0]
        all_datasets = Package.search_by_name('')

        if search_mode.lower() == 'column':            
            search_results = ColumnSearchHelper.run(
                search_filters=search_filters, 
                search_phrase=search_phrase, 
                search_results=search_results
                )
            
            return search_results
        
        elif search_mode.lower() == 'sample' and SearchHelper.check_plugin_enabled("sample_link"):            
            search_results = SampleSearchHelper.run(datasets=all_datasets, 
                search_filters=search_filters, 
                search_phrase=search_phrase, 
                search_results=search_results
                )
            return search_results
        
        elif search_mode.lower() == 'resource_metadata':
            search_results = ExtraMetadataSearchHelper.run(
                datasets=all_datasets,
                target_metadata_name=target_metadata,
                search_filters=search_filters, 
                search_phrase=search_phrase, 
                search_results=search_results
            )
            return search_results
        
        elif search_mode.lower() == 'publication':
            search_results = PublicationSearchHelper.run(
                datasets=all_datasets,                
                search_filters=search_filters, 
                search_phrase=search_phrase, 
                search_results=search_results
            )
            return search_results
        
        else:
            return search_results



    def after_delete(self, context, pkg_dict):
        dataset = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
        # for resource in dataset['resources']:
        #     column_indexer = DataResourceColumnIndex()
        #     records = column_indexer.get_by_resource(id=resource['id'])
        #     for rec in records:
        #         rec.delete()
        #         rec.commit()

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
            if SearchHelper.is_csv(resource):
                dataframe_columns, fit_for_autotag = SearchHelper.get_csv_columns(resource['id'])
                columns_names = ""
                for col in dataframe_columns:
                    columns_names += (col + ",")
                # column_indexer = DataResourceColumnIndex(resource_id=resource['id'], columns_names=columns_names)
                # column_indexer.save()
            
            elif SearchHelper.is_xlsx(resource):
                xls_dataframes_columns = SearchHelper.get_xlsx_columns(resource['id'])
                columns_names = ""
                for sheet, columns_object in xls_dataframes_columns.items():
                    for col in columns_object[0]:  
                        columns_names += (col + ",")
                
                # column_indexer = DataResourceColumnIndex(resource_id=resource['id'], columns_names=columns_names)
                # column_indexer.save()
  
        return resource



    def before_delete(self, context, resource, resources):
        if not SearchHelper.is_csv(resource) and not SearchHelper.is_xlsx(resource):
            return resource
        # column_indexer = DataResourceColumnIndex()
        # records = column_indexer.get_by_resource(id=resource['id'])
        # for rec in records:
        #     rec.delete()
        #     rec.commit()
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