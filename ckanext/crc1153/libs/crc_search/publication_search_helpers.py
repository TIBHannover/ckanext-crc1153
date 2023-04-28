# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper
from ckanext.crc1153.libs.crc_search.facet_helpers import FacetHelper
from ckanext.crc1153.libs.auth_helpers import AuthHelpers
from ckanext.crc1153.libs.commons import Commons
from sqlalchemy.sql.expression import false
from ckan.model import Package
from sklearn.feature_extraction.text import TfidfVectorizer
if Commons.check_plugin_enabled("dataset_reference"):
    from ckanext.dataset_reference.models.package_reference_link import PackageReferenceLink


SIMILARITY_MEASURE_THRESHOLD = 0.7


class PublicationSearch():

    @staticmethod
    def run(search_query, search_params, search_results):
        search_phrase = search_query.split('publication:')[1].strip().lower()
        search_results, search_filters = SearchHelper.empty_ckan_search_result(search_results, search_params)
        datasets = Package.search_by_name('')
        search_results = PublicationSearch.publication_search(datasets, search_phrase, search_filters, search_results)        
        return search_results



    @staticmethod
    def publication_search(datasets, search_phrase, search_filters, search_results):
        pub_model = PackageReferenceLink({})
        for package in datasets:
            if package.state != 'active' or not AuthHelpers.check_access_show_package(package.id):
                continue
            
            #  If search triggers from an organization page.
            if SearchHelper.dataset_is_not_in_selected_organization(search_filters, package.owner_org):
                continue            
            
            # If search triggers from a group page.
            if SearchHelper.dataset_is_not_in_selected_group(search_filters, package.get_groups()):
                continue
            
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            detected = False            
            linked_publications = pub_model.get_by_package(name=dataset['name'])
            if linked_publications == false:
                continue

            for pub in linked_publications:                
                if not pub.citation:
                    continue                                
                elif PublicationSearch.similarity_calc(search_phrase.lower(), pub.citation.lower()) >= SIMILARITY_MEASURE_THRESHOLD:
                    if not detected:
                        search_results['search_facets'] = FacetHelper.update_search_facet_with_dataset(search_results['search_facets'], dataset)                        
                        search_results = SearchHelper.add_dataset_to_search_result(dataset, search_filters, search_results)
                    detected = True 
                elif search_phrase.lower() in pub.citation.lower():
                    tokens = search_phrase.split(' ')
                    for tok in tokens:
                        if tok.lower() in pub.citation.lower():
                            if not detected:
                                search_results['search_facets'] = FacetHelper.update_search_facet_with_dataset(search_results['search_facets'], dataset)                                
                                search_results = SearchHelper.add_dataset_to_search_result(dataset, search_filters, search_results)
                            detected = True 
                            break


        return search_results



    @staticmethod
    def similarity_calc(query, doc):
        corpus = [query, doc]
        vectorModel = TfidfVectorizer(min_df=1)
        tfidf = vectorModel.fit_transform(corpus)
        similarities = tfidf * tfidf.T       
        return float(similarities.toarray()[0][1])
    

    
