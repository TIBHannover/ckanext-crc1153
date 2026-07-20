import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from ckanext.crc1153.libs.crc_search.data_column_helpers import ColumnSearch
from ckanext.crc1153.libs.crc_search.sample_search_helpers import SampleSearch
from ckanext.crc1153.libs.crc_search.publication_search_helpers import PublicationSearch
from ckanext.crc1153.libs.crc_search.extra_metadata_helpers import ExtraMetadataSearch
from ckanext.crc1153.libs.crc_search.file_helpers import FileHelper
from ckanext.crc1153.libs.crc_search.indexer_helper import IndexerHelper
from ckanext.crc1153.libs.commons import Commons
from ckanext.crc1153.models.data_resource_column_index import DataResourceColumnIndex
from flask import Blueprint


log = logging.getLogger(__name__)


class CrcSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IBlueprint)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, '../templates')


    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.add_url_rule(
            u'/crc_search/indexer',
            u'indexer',
            IndexerHelper.indexer,
            methods=['GET']
            )

        return blueprint


    # IPackageController

    def after_dataset_search(self, search_results, search_params):
        try:
            search_types = ['column', 'publication', 'sample', 'material_combination', 'demonstrator', 'manufacturing_process', 'analysis_method']
            extra_metadata = ['material_combination', 'demonstrator', 'manufacturing_process', 'analysis_method']
            search_query = search_params.get('q', '').lower()
            if search_query.split(':')[0].lower() not in search_types:
                return search_results

            elif len(search_query.split('column:')) > 1:
                search_results = ColumnSearch.run(search_query=search_query, search_params=search_params, search_results=search_results)

            elif len(search_query.split('publication:')) > 1 and Commons.check_plugin_enabled("dataset_reference"):
                search_results = PublicationSearch.run(search_query=search_query, search_params=search_params, search_results=search_results)

            elif len(search_query.split('sample:')) > 1 and Commons.check_plugin_enabled("sample_link"):
                search_results = SampleSearch.run(search_query=search_query, search_params=search_params, search_results=search_results)

            elif search_query.split(':')[0].strip() in extra_metadata and Commons.check_plugin_enabled("crc1153_specific_metadata"):
                target_metadata = search_query.split(':')[0].strip()
                search_results = ExtraMetadataSearch.run(search_query=search_query, search_params=search_params, target_metadata_name=target_metadata, search_results=search_results)
            else:
                return search_results

            return search_results

        except Exception:
            log.exception("CRC1153 special search failed")
            return search_results


    def after_search(self, search_results, search_params):
        return self.after_dataset_search(search_results, search_params)

    def after_dataset_delete(self, context, pkg_dict):
        resources = pkg_dict.get('resources')
        if resources is None and pkg_dict.get('id'):
            try:
                dataset = toolkit.get_action('package_show')({}, {'name_or_id': pkg_dict['id']})
                resources = dataset.get('resources', [])
            except Exception:
                log.exception("CRC1153 column index cleanup failed for deleted dataset")
                resources = []
        for resource in resources or []:
            self._delete_resource_index(resource.get('id'))

        return pkg_dict

    def after_delete(self, context, data):
        if isinstance(data, list):
            return data
        return self.after_dataset_delete(context, data)

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_dataset_create(self, context, pkg_dict):
        return pkg_dict

    def after_dataset_update(self, context, pkg_dict):
        return pkg_dict

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
        self._index_resource(resource)
        return resource


    def before_resource_delete(self, context, resource, resources):
        if not FileHelper.is_csv(resource) and not FileHelper.is_xlsx(resource):
            return resource
        self._delete_resource_index(resource.get('id'))
        return resources


    def after_resource_delete(self, context, resources):
        return resources

    def before_resource_create(self, context, resource):
        return resource

    def before_resource_update(self, context, current, resource):
        return resource

    def after_resource_update(self, context, resource):
        return resource

    def before_resource_show(self, resource_dict):
        return resource_dict

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

    @staticmethod
    def _index_resource(resource):
        if resource.get('url_type') != 'upload':
            return

        if FileHelper.is_csv(resource):
            dataframe_columns, _ = FileHelper.get_csv_columns(resource['id'])
            columns_names = ",".join(str(col) for col in dataframe_columns)
        elif FileHelper.is_xlsx(resource):
            xls_dataframes_columns = FileHelper.get_xlsx_columns(resource['id'])
            columns = []
            for columns_object in xls_dataframes_columns.values():
                columns.extend(str(col) for col in columns_object[0])
            columns_names = ",".join(columns)
        else:
            return

        column_indexer = DataResourceColumnIndex(
            resource_id=resource['id'],
            columns_names=columns_names,
        )
        column_indexer.save()

    @staticmethod
    def _delete_resource_index(resource_id):
        if not resource_id:
            return
        records = DataResourceColumnIndex.get_by_resource(id=resource_id)
        for rec in records or []:
            rec.delete()
            rec.commit()
