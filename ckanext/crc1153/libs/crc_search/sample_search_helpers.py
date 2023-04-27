# encoding: utf-8


import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
from ckanext.crc1153.libs.crc_search.facet_helpers import FacetHelper
from ckanext.crc1153.libs.commons import Commons
from ckan.model import Package
if Commons.check_plugin_enabled("sample_link"):
    from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper


class SampleSearchHelper():


    @staticmethod
    def run(search_query, search_params, search_results):
        search_phrase = search_query.split('sample:')[1].strip().lower()
        search_results, search_filters = SearchHelper.empty_ckan_search_result(search_results, search_params)
        datasets = Package.search_by_name('')
        search_results = SampleSearchHelper.sample_search(datasets, search_phrase, search_filters, search_results)        
        toolkit.g.detected_resources_ids = search_results['detected_resources_ids']
        return search_results



    @staticmethod
    def sample_search(datasets, search_phrase, search_filters, search_results):
        for package in datasets:
            if package.state != 'active' or not SearchHelper.check_access_package(package.id):
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
                samples = list(SampleLinkHelper.get_sample_link(res['id']).keys())
                for name in samples:
                    if search_phrase in name.lower():
                        if not detected:
                            search_results['search_facets'] = FacetHelper.update_search_facet_with_dataset(search_results['search_facets'], dataset)
                            search_results = SearchHelper.add_search_result(dataset, search_filters, search_results)                            
                        detected = True
                        if res['id'] not in search_results['detected_resources_ids']:
                            search_results['detected_resources_ids'].append(res['id'])
                        break

        return search_results