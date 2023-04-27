# encoding: utf-8

from this import d
import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
from sqlalchemy.sql.expression import false
import re
from sklearn.feature_extraction.text import TfidfVectorizer
if SearchHelper.check_plugin_enabled("dataset_reference"):
    from ckanext.dataset_reference.models.package_reference_link import PackageReferenceLink



class PublicationSearchHelper():

    @staticmethod
    def run(datasets, search_phrase, search_filters, search_results):
        '''
            Run the search for dataset that are link to a publication based on the search term.

            Args:
                - datasets: the target datasets to search in. 
                - search_phrase: the search input
                - search_filters: the ckan search facets dictionary (search_params['fq'][0])
                - search_results: the ckan search results dictionary.
            
            Return:
                - search_results dictionary
        '''

        pub_model = PackageReferenceLink({})
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
            linked_publications = pub_model.get_by_package(name=dataset['name'])
            if linked_publications == false:
                continue

            for pub in linked_publications:                
                if not pub.citation:
                    continue                                
                elif PublicationSearchHelper.similarity_calc(search_phrase.lower(), pub.citation.lower()) >= 0.7:
                    if not detected:
                        search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                        search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                        search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                        search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                        search_results = SearchHelper.add_search_result(dataset, search_filters, search_results)
                    detected = True 
                elif search_phrase.lower() in pub.citation.lower():
                    tokens = search_phrase.split(' ')
                    for tok in tokens:
                        if tok.lower() in pub.citation.lower():
                            if not detected:
                                search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                                search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                                search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                                search_results['search_facets'] = SearchHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                                search_results = SearchHelper.add_search_result(dataset, search_filters, search_results)
                            detected = True 
                            break
        
        return search_results

    

    @staticmethod
    def similarity_calc(query, doc):
        '''
            Calculate the similarity between the search input and the target doc.

            Args:
                - query: Input search query
                - doc: the target doc
            
            Return:
                - The similartiy score
        '''

        corpus = [query, doc]
        vectorModel = TfidfVectorizer(min_df=1)
        tfidf = vectorModel.fit_transform(corpus)
        similarities = tfidf * tfidf.T       
        return float(similarities.toarray()[0][1])
    

    
