# encoding: utf-8


import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
from ckan.model import Package
if SearchHelper.check_plugin_enabled("sample_link"):
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
            
            # only consider dataset in an organization. If search triggers from an organization page.
            if 'owner_org' in search_filters:
                owner_org_id = search_filters.split('owner_org:')[1]
                if ' ' in owner_org_id:
                    owner_org_id = owner_org_id.split(' ')[0]                    
                if '"' + package.owner_org + '"' != owner_org_id:
                    continue
            
            # only consider dataset in a group. If search triggers from a group page.
            if 'groups' in search_filters:
                this_dataset_groups = package.get_groups()
                target_group_title = search_filters.split('groups:')[1]
                if ' ' in target_group_title:
                    target_group_title = target_group_title.split(' ')[0]
                is_part_of_group = False
                for g in this_dataset_groups:
                    if '"' + g.name + '"' == target_group_title:
                        is_part_of_group = True
                        break
                if not is_part_of_group:
                    continue
            
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            detected = False

            for res in dataset['resources']:
                samples = list(SampleLinkHelper.get_sample_link(res['id']).keys())
                for name in samples:
                    if search_phrase in name.lower():
                        if not detected:
                            search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                            search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                            search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                            search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                            search_results = SearchHelper.add_search_result(dataset, search_filters, search_results)                            
                        detected = True
                        search_results['detected_resources_ids'].append(res['id'])
                        break

        return search_results