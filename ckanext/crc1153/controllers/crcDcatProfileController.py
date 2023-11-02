# encoding: utf-8

from flask import render_template
import ckan.plugins.toolkit as toolkit
from ckan.model import Package
from ckanext.dcat.processors import RDFSerializer
from xml.etree import ElementTree
from flask import send_file
import io
from ckanext.crc1153.libs.crc_profile.helpers import Crc1153DcatProfileHelper as Helper
from ckanext.crc1153.libs.auth_helpers import AuthHelpers
from ckan.model import Package
import json



class Crc1153DcatProfileController:


    def load_admin_view():
        AuthHelpers.abort_if_not_admin()
        return render_template('crc_profile/admin_panel.html')
    


    
    def push_to_sparql():
        AuthHelpers.abort_if_not_admin()
        all_datasets = Package.search_by_name('')
        all_graphs = []
        for dataset in all_datasets:
            if dataset.state == 'active':
                package = toolkit.get_action('package_show')({}, {'name_or_id': dataset.name})
                package = Helper.setDatasetUri(package)   
                graph = Helper.get_dataset_graph(package)
                all_graphs.append(graph)


        toolkit.enqueue_job(push_catalog_to_sparql, kwargs={'catalog_graphs': all_graphs})
                
        return json.dumps({"_result": True})
    


    def delete_from_sparql():
        AuthHelpers.abort_if_not_admin()
        all_datasets = Package.search_by_name('')
        all_graphs = []
        for dataset in all_datasets:
            if dataset.state == 'active':
                package = toolkit.get_action('package_show')({}, {'name_or_id': dataset.name})
                package = Helper.setDatasetUri(package)   
                graph = Helper.get_dataset_graph(package)
                all_graphs.append(graph)


        toolkit.enqueue_job(delete_catalog_from_sparql, kwargs={'catalog_graphs': all_graphs})
                
        return json.dumps({"_result": True})
    
    
    
    def export_catalog():
        AuthHelpers.abort_if_not_admin()

        ElementTree.register_namespace("dc", "http://purl.org/dc/terms/")
        ElementTree.register_namespace("dct", "http://purl.org/dc/dcmitype/")
        ElementTree.register_namespace("dcat", "http://www.w3.org/ns/dcat#")
        ElementTree.register_namespace("foaf", "http://xmlns.com/foaf/0.1/")
        ElementTree.register_namespace("schemaorg", "https://schema.org/")
        ElementTree.register_namespace("emno", "http://emmo.info/emmo/")
        ElementTree.register_namespace("tema", "https://www.tib.eu/tema/")
        ElementTree.register_namespace("envo", "http://purl.obolibrary.org/obo/envo/")
        ElementTree.register_namespace("ncit", "http://purl.obolibrary.org/obo/ncit/")
        ElementTree.register_namespace("vcard", "http://www.w3.org/2006/vcard/ns#")
        ElementTree.register_namespace("owl", "http://www.w3.org/2002/07/owl#")
        ElementTree.register_namespace("adms", "http://www.w3.org/ns/adms#")
        ElementTree.register_namespace("time", "http://www.w3.org/2006/time")
        ElementTree.register_namespace("locn", "http://www.w3.org/ns/locn#")
        ElementTree.register_namespace("gsp", "http://www.opengis.net/ont/geosparql#")
        ElementTree.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        ElementTree.register_namespace("dr", "http://www.w3id.org/ecsel-dr-PROD#")
        

        all_datasets = Package.search_by_name('')
        xml = ElementTree.fromstring("<RDF></RDF>")
        dataset_dicts = []
        for dataset in all_datasets:
            if dataset.state == 'active':                
                package = toolkit.get_action('package_show')({}, {'name_or_id': dataset.name})
                package = Helper.setDatasetUri(package)                                                              
                dataset_dicts.append(package)
                
        serializer = RDFSerializer(profiles=package.get('profiles'))
        rdf_output = serializer.serialize_catalog(dataset_dicts=dataset_dicts, _format="ttl")        
        file = io.BytesIO(rdf_output.encode())        
        return send_file(file, mimetype='application/ttl', attachment_filename="ckancatlog.ttl", as_attachment = True)
    




def push_catalog_to_sparql(catalog_graphs):
    for graph in catalog_graphs:
        try:
            res_d = Helper.delete_from_sparql(graph)
            res_i = Helper.insert_to_sparql(graph)
        except:
            continue



def delete_catalog_from_sparql(catalog_graphs):
    for graph in catalog_graphs:
        try:
            res_d = Helper.delete_from_sparql(graph)            
        except:
            continue