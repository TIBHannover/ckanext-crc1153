# encoding: utf-8


import ckan.plugins.toolkit as toolkit
from ckan.model import Package
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
from ckanext.crc1153.libs.crc_search.facet_helpers import FacetHelper
from ckanext.crc1153.libs.auth_helpers import AuthHelpers


class ExtraMetadataSearchHelper():


    @staticmethod
    def run(search_query, search_params, target_metadata_name, search_results):
        query_splitor = target_metadata_name + ":"
        search_phrase = search_query.split(query_splitor)[1].strip().lower()
        search_results, search_filters = SearchHelper.empty_ckan_search_result(search_results, search_params)
        datasets = Package.search_by_name('')
        search_results = ExtraMetadataSearchHelper.crc_metadata_search(datasets, target_metadata_name, search_phrase, search_filters, search_results)
        toolkit.g.detected_resources_ids = search_results['detected_resources_ids']       
        return search_results
    


    @staticmethod
    def crc_metadata_search(datasets, target_metadata_name, search_phrase, search_filters, search_results):        
        for package in datasets:
            if package.state != 'active' or not AuthHelpers.check_access_show_package(package.id):
                continue
            
            # If search triggers from an organization page.
            if SearchHelper.dataset_is_not_in_selected_organization(search_filters, package.owner_org):
                continue           
            
            # If search triggers from a group page.
            if SearchHelper.dataset_is_not_in_selected_group(search_filters, package.get_groups()):
                continue           

            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})            
            detected = False

            for res in dataset['resources']:               
                if res.get(target_metadata_name) and search_phrase.lower() in res.get(target_metadata_name).lower():                                         
                        if not detected:
                            search_results['search_facets'] = FacetHelper.update_search_facet_with_dataset(search_results['search_facets'], dataset)                            
                            search_results = SearchHelper.add_search_result(dataset, search_filters, search_results)                            
                        detected = True
                        search_results['detected_resources_ids'].append(res['id'])
                        break

        return search_results