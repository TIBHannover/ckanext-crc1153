# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
from ckanext.crc1153.libs.crc_search.facet_helpers import FacetHelper
from ckanext.crc1153.models.data_resource_column_index import DataResourceColumnIndex



class ColumnSearch():

    @staticmethod
    def run(search_query, search_params, search_results):
        search_phrase = search_query.split('column:')[1].strip().lower()
        search_results, search_filters = SearchHelper.empty_ckan_search_result(search_results, search_params)
        search_results = ColumnSearch.column_search(search_phrase, search_filters, search_results)        
        toolkit.g.detected_resources_ids = search_results['detected_resources_ids']
        return search_results
    


    @staticmethod
    def column_search(search_phrase, search_filters, search_results):
        column_indexer_model = DataResourceColumnIndex()
        all_indexes = column_indexer_model.get_all()
        already_included_datasets = []  
        for record in all_indexes:
            resource_id = record.resource_id
            resource_index_value = record.columns_names                    
            if search_phrase.lower() in resource_index_value.lower():
                if SearchHelper.skip_if_not_authorized(resource_id):
                    continue
                
                resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
                dataset = toolkit.get_action('package_show')({}, {'name_or_id': resource['package_id']})
                
                # If search triggers from an organization page.
                if SearchHelper.dataset_is_not_in_selected_organization(search_filters, dataset['owner_org']):
                    continue
                
                # If search triggers from a group page.
                if SearchHelper.dataset_is_not_in_selected_group(search_filters, dataset['groups']):
                    continue
                
                if dataset['id'] not in already_included_datasets:            
                    search_results['search_facets'] = FacetHelper.update_search_facet_with_dataset(search_results['search_facets'], dataset)                    
                    search_results = SearchHelper.add_dataset_to_search_result(dataset, search_filters, search_results)
                    already_included_datasets.append(dataset['id'])
                
                search_results['detected_resources_ids'].append(resource_id)

        return search_results
    
    

   
