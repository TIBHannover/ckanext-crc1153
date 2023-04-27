# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
from ckanext.crc1153.models.data_resource_column_index import DataResourceColumnIndex



class ColumnSearchHelper():

    @staticmethod
    def run(search_query, search_params, search_results):
        search_phrase = search_query.split('column:')[1].strip().lower()
        search_results, search_filters = SearchHelper.empty_ckan_search_result(search_results, search_params)
        search_results = ColumnSearchHelper.column_search(search_phrase, search_filters, search_results)        
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
                if SearchHelper.skip_data(resource_id):
                    continue
                
                resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
                dataset = toolkit.get_action('package_show')({}, {'name_or_id': resource['package_id']})
                
                # only consider dataset in an organization. If search triggers from an organization page.
                if 'owner_org' in search_filters:
                    owner_org_id = search_filters.split('owner_org:')[1]
                    if ' ' in owner_org_id:
                        owner_org_id = owner_org_id.split(' ')[0]                    
                    if '"' + dataset['owner_org'] + '"' != owner_org_id:
                        continue
                

                # only consider dataset in a group. If search triggers from a group page.
                if 'groups' in search_filters:
                    this_dataset_groups = dataset['groups']                    
                    target_group_title = search_filters.split('groups:')[1]                                      
                    if ' ' in target_group_title:
                        target_group_title = target_group_title.split(' ')[0]
                    is_part_of_group = False
                    for g in this_dataset_groups:
                        if '"' + g['name'] + '"' == target_group_title:
                            is_part_of_group = True
                            break
                    if not is_part_of_group:
                        continue

                
                if dataset['id'] not in already_included_datasets:            
                    search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                    search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                    search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                    search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                    search_results = SearchHelper.add_search_result(dataset, search_filters, search_results)
                    already_included_datasets.append(dataset['id'])
                
                search_results['detected_resources_ids'].append(resource_id)

        return search_results
    
    

   
