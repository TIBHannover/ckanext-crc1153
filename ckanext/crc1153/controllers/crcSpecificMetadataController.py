# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from flask import render_template, request, redirect
import ckan.lib.helpers as h
from ckanext.crc1153.libs.commons import Commons
from ckanext.crc1153.libs.crc_specific_metadata.helpers import CrcSpecificMetadataHelpers



class CrcSpecificMetadataController:


    def render_add_metadata_page(package_id):        
        package = toolkit.get_action('package_show')({}, {'name_or_id': package_id})
        stages = True    
        resources = package['resources']
        custom_metadata_fields = {'material_combination': [], 'demonstrator': [], 'manufacturing_process': [], 'analysis_method': []}
        for meta in custom_metadata_fields.keys():
            for res in resources:
                if  meta in res.keys() and res[meta] and res[meta] != '':
                    custom_metadata_fields[meta].append(res[meta])

        for meta in custom_metadata_fields.keys():
            custom_metadata_fields[meta] = list(set( custom_metadata_fields[meta]))



        return render_template('crc_specific_metadata/add_view.html', 
            pkg_dict=package, 
            custom_stage=stages,
            custom_metadata_fields=custom_metadata_fields,
            material_list=CrcSpecificMetadataHelpers.get_material_list()
        )



    def save_metadata():
        metadata_fields = ['material_combination', 'demonstrator', 'manufacturing_process', 'analysis_method']
        resource_count = request.form.get('resources_count')
        package_name = request.form.get('pkg_name')
        
        try:
            for field in metadata_fields:
                custom_metadata_fields_length = request.form.get('processed_metadata_' + field)
                for i in range(1, int(resource_count) + int(custom_metadata_fields_length) + 1):
                    resource_ids = request.form.getlist('custom_metadata_' + field + '_' + str(i))
                    field_text = request.form.get(field + '_' + str(i))

                    for res_id in resource_ids:                       
                        resource = toolkit.get_action('resource_show')({}, {'id': res_id})
                        resource[field] = field_text
                        toolkit.get_action('resource_update')({}, resource)
        
        except:
            # raise
            return toolkit.abort(500, "")

        if Commons.check_plugin_enabled("media_wiki"):
            return redirect(h.url_for('semantic_media_wiki.machines_view', id=str(package_name) ,  _external=True)) 

        return redirect(h.url_for('dataset.read', id=str(package_name) ,  _external=True))

    