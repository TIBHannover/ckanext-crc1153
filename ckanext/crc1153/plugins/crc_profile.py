import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from flask import Blueprint
from ckanext.crc1153.controllers.crcDcatProfileController import Crc1153DcatProfileController
from ckanext.crc1153.libs.crc_profile.helpers import Crc1153DcatProfileHelper as Helper


log = logging.getLogger(__name__)


class Dcatapcrc1153Plugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, '../templates')
        toolkit.add_public_directory(config_, '../public')
        toolkit.add_resource('../public/crc_profile', 'ckanext-crc1153-profile')
        config_.setdefault(
            'ckanext.dcat.rdf.profiles',
            'euro_dcat_ap_2 crc1153_dcat_ap',
        )


    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.add_url_rule(
            u'/dcatapcrc1153/load_admin_view',
            u'load_admin_view',
            Crc1153DcatProfileController.load_admin_view,
            methods=['GET']
            )

        blueprint.add_url_rule(
            u'/dcatapcrc1153/export_catalog',
            u'export_catalog',
            Crc1153DcatProfileController.export_catalog,
            methods=['GET']
            )

        blueprint.add_url_rule(
            u'/dcatapcrc1153/push_to_sparql',
            u'push_to_sparql',
            Crc1153DcatProfileController.push_to_sparql,
            methods=['GET']
            )

        blueprint.add_url_rule(
            u'/dcatapcrc1153/delete_from_sparql',
            u'delete_from_sparql',
            Crc1153DcatProfileController.delete_from_sparql,
            methods=['GET']
            )

        return blueprint


    # IPackageController


    def after_dataset_create(self, context, pkg_dict):
        '''
            Post the dataset metadata to the sparql endpoint
        '''

        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
            graph = Helper.get_dataset_graph(package)
            Helper.insert_to_sparql(graph)
        except Exception:
            log.exception("Failed to insert CRC1153 dataset metadata into SPARQL")
            return pkg_dict

        return pkg_dict



    def after_dataset_update(self, context, pkg_dict):
        '''
            Upadte an existing dataset metadata on the sparql endpoint
        '''

        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
            graph = Helper.get_dataset_graph(package)
            Helper.delete_from_sparql(graph)
            Helper.insert_to_sparql(graph)
        except Exception:
            log.exception("Failed to update CRC1153 dataset metadata in SPARQL")
            return pkg_dict

        return pkg_dict



    def after_dataset_delete(self, context, pkg_dict):
        '''
            Delete an existing dataset metadata on the sparql endpoint
        '''

        try:
            package = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
            graph = Helper.get_dataset_graph(package)
            Helper.delete_from_sparql(graph)
        except Exception:
            log.exception("Failed to delete CRC1153 dataset metadata from SPARQL")
            return pkg_dict

        return pkg_dict



    def after_dataset_search(self, search_results, search_params):
        return search_results

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_dataset_show(self, context, pkg_dict):
        return pkg_dict

    def before_dataset_search(self, search_params):
        return search_params

    def before_dataset_index(self, pkg_dict):
        return pkg_dict

    def before_dataset_view(self, pkg_dict):
        return pkg_dict

    def after_create(self, context, data):
        if self._is_resource_dict(data):
            return self.after_resource_create(context, data)
        return self.after_dataset_create(context, data)

    def after_update(self, context, data):
        if self._is_resource_dict(data):
            return self.after_resource_update(context, data)
        return self.after_dataset_update(context, data)

    def after_delete(self, context, data):
        if isinstance(data, list):
            return self.after_resource_delete(context, data)
        return self.after_dataset_delete(context, data)

    def after_search(self, search_results, search_params):
        return self.after_dataset_search(search_results, search_params)

    def after_show(self, context, pkg_dict):
        return self.after_dataset_show(context, pkg_dict)

    def before_search(self, search_params):
        return self.before_dataset_search(search_params)

    def before_index(self, pkg_dict):
        return self.before_dataset_index(pkg_dict)

    def before_view(self, pkg_dict):
        return self.before_dataset_view(pkg_dict)



     # IResourceController

    def after_resource_create(self, context, resource):
        return resource

    def after_resource_update(self, context, resource):
        try:
            package = {}
            if resource.get("package_id"):
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource['package_id']})
            elif resource.get('name'):
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource['name']})

            graph = Helper.get_dataset_graph(package)
            Helper.delete_from_sparql(graph)
            Helper.insert_to_sparql(graph)
        except Exception:
            log.exception("Failed to update CRC1153 resource metadata in SPARQL")
            return resource

        return resource



    def before_resource_delete(self, context, resource, resources):
        try:
            package = {}
            resource_dict = toolkit.get_action('resource_show')({}, {'id': resource['id']})
            if resource_dict.get("package_id"):
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource_dict['package_id']})
            elif resource_dict.get('name'):
                package = toolkit.get_action('package_show')({}, {'name_or_id': resource_dict['name']})

            graph = Helper.get_dataset_graph(package)
            Helper.delete_from_sparql(graph)
        except Exception:
            log.exception("Failed to delete CRC1153 resource metadata from SPARQL")
            return resource
        return resources


    def before_resource_create(self, context, resource):
        return resource

    def before_resource_update(self, context, current, resource):
        return resource


    def before_resource_show(self, resource_dict):
        return resource_dict

    def after_resource_delete(self, context, resources):
        return resources

    def before_create(self, context, resource):
        return self.before_resource_create(context, resource)

    def before_update(self, context, current, resource):
        return self.before_resource_update(context, current, resource)

    def before_delete(self, context, resource, resources):
        return self.before_resource_delete(context, resource, resources)

    def before_show(self, resource_dict):
        return self.before_resource_show(resource_dict)

    @staticmethod
    def _is_resource_dict(data):
        return isinstance(data, dict) and (
            'package_id' in data or 'url_type' in data or 'resource_type' in data
        )

