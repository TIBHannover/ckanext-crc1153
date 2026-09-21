# encoding: utf-8


import logging

import ckan.plugins.toolkit as toolkit
from sqlalchemy.sql.expression import false
from SPARQLWrapper import SPARQLWrapper, POST
from ckanext.dcat.processors import RDFSerializer
from ckanext.crc1153.libs.commons import Commons


log = logging.getLogger(__name__)

DEFAULT_DCAT_PROFILES = ['euro_dcat_ap_2', 'crc1153_dcat_ap']



class Crc1153DcatProfileHelper():


    def get_apache_jena_endpoint():
        return toolkit.config.get('ckanext.apacheJena.endpoint')



    def get_linked_publication(dataset_name):
        '''
            The functions get all the linked publications for a dataset in ckan.

            Args:
                - dataset_name: The target dataset name.
            Returns:
                - The publication citation
        '''

        if not Commons.check_plugin_enabled("dataset_reference"):
            return None

        PackageReferenceLink = Crc1153DcatProfileHelper._package_reference_model()
        if PackageReferenceLink is None:
            return None

        linked_pubs = []
        res_object = PackageReferenceLink({})
        result = res_object.get_by_package(name=dataset_name)
        if result != false:
            for res in result:
                linked_pubs.append(res.citation)

        return linked_pubs



    @staticmethod
    def get_linked_machines(resource_id):
        if not Commons.check_plugin_enabled("machine_link"):
            return {}
        mediaWikiHelper = Crc1153DcatProfileHelper._machine_link_helper()
        if mediaWikiHelper is None:
            return {}
        # a dict of machines [machine_name:machine_link]
        return mediaWikiHelper.get_machine_link(resource_id)



    @staticmethod
    def get_linked_samples(resource_id):
        if not Commons.check_plugin_enabled("sample_link"):
            return {}
        SampleLinkHelper = Crc1153DcatProfileHelper._sample_link_helper()
        if SampleLinkHelper is None:
            return {}

        # a dict of samples [sample_name:sample_link]
        return SampleLinkHelper.get_sample_link(resource_id)



    @staticmethod
    def insert_to_sparql(graph):
        endpoint = Crc1153DcatProfileHelper.get_apache_jena_endpoint()
        if not endpoint:
            log.warning("No Apache Jena endpoint configured; skipping SPARQL insert")
            return None
        results = None
        for s,p,o in graph:
            s,p,o = Crc1153DcatProfileHelper.clean_triples(s,p,o)
            query = 'INSERT DATA{ ' + s + ' ' + p + ' ' + o + ' .  }'
            sparql = SPARQLWrapper(endpoint)
            sparql.setMethod(POST)
            sparql.setQuery(query)
            results = sparql.query()

        return results



    @staticmethod
    def delete_from_sparql(graph):
        endpoint = Crc1153DcatProfileHelper.get_apache_jena_endpoint()
        if not endpoint:
            log.warning("No Apache Jena endpoint configured; skipping SPARQL delete")
            return None
        results = None
        for s,p,o in graph:
            s,p,o = Crc1153DcatProfileHelper.clean_triples(s,p,o)
            query = ""
            if "_:N" in o:
                # blank node as object
                query = 'DELETE{ ' + s + ' ' + p + ' ?bnode . ?bnode ?p ?o .} WHERE{ '  + s + ' ' + p + ' ?bnode . ?bnode ?p ?o . FILTER (isBlank(?bnode))}'
                sparql = SPARQLWrapper(endpoint)
                sparql.setMethod(POST)
                sparql.setQuery(query)
                results = sparql.query()
            elif "_:N" not in s and "_:N" not in p:
                query = 'DELETE WHERE{ ' + s + ' ' + p + ' ?anything .  }'
                sparql = SPARQLWrapper(endpoint)
                sparql.setMethod(POST)
                sparql.setQuery(query)
                results = sparql.query()


        return results



    @staticmethod
    def get_dataset_graph(dataset_dict):
        dataset_dict = Crc1153DcatProfileHelper.setDatasetUri(dataset_dict)
        serializer = RDFSerializer(
            profiles=Crc1153DcatProfileHelper.get_rdf_profiles(dataset_dict)
        )
        gr_dataset = serializer.graph_from_dataset(dataset_dict)
        return  serializer.g



    @staticmethod
    def clean_triples(s,p,o):
        return [
            Crc1153DcatProfileHelper._sparql_term(s),
            Crc1153DcatProfileHelper._sparql_term(p),
            Crc1153DcatProfileHelper._sparql_term(o),
        ]




    @staticmethod
    def setDatasetUri(package):
        ckan_root_path = toolkit.config.get('ckan.root_path')
        ckan_base_url = toolkit.config.get('ckan.site_url')
        if ckan_root_path:
            ckan_root_path = ckan_root_path.split("/{{LANG}}")[0]
            package["uri"] = ckan_base_url + ckan_root_path + "/dataset/" + package['id']
            for res in package['resources']:
                res["uri"] = ckan_base_url + ckan_root_path + "/dataset/" + package['name'] + "/resource/" + res['id']
        else:
            package["uri"] = ckan_base_url + "/dataset/" + package['id']
            for res in package['resources']:
                res["uri"] = ckan_base_url + "/dataset/" + package['name'] + "/resource/" + res['id']

        return package

    @staticmethod
    def get_rdf_profiles(dataset_dict=None):
        profiles = dataset_dict.get('profiles') if dataset_dict else None
        if not profiles:
            profiles = toolkit.config.get('ckanext.dcat.rdf.profiles')

        if isinstance(profiles, str):
            profiles = profiles.split()
        elif profiles:
            profiles = list(profiles)
        else:
            profiles = list(DEFAULT_DCAT_PROFILES)

        if 'crc1153_dcat_ap' not in profiles:
            profiles.append('crc1153_dcat_ap')

        return profiles

    @staticmethod
    def _sparql_term(term):
        if hasattr(term, 'n3'):
            return term.n3()
        term = str(term)
        if term.startswith('N'):
            return '_:' + term
        if term.startswith('http'):
            return '<' + term + '>'
        return "'" + term.replace('\\', '\\\\').replace("'", "\\'") + "'"

    @staticmethod
    def _package_reference_model():
        try:
            from ckanext.dataset_reference.models.package_reference_link import PackageReferenceLink
            return PackageReferenceLink
        except ImportError:
            log.warning("dataset_reference plugin is enabled but not importable")
            return None

    @staticmethod
    def _machine_link_helper():
        try:
            from ckanext.semantic_media_wiki.libs.media_wiki import Helper
            return Helper
        except ImportError:
            log.warning("machine_link plugin is enabled but not importable")
            return None

    @staticmethod
    def _sample_link_helper():
        try:
            from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper
            return SampleLinkHelper
        except ImportError:
            log.warning("sample_link plugin is enabled but not importable")
            return None



