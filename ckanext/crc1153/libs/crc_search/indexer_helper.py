# encoding: utf-8

from ckan.model import Package
from ckanext.crc1153.models.data_resource_column_index import DataResourceColumnIndex
from ckanext.crc1153.libs.auth_helpers import AuthHelpers
from ckanext.crc1153.libs.crc_search.search_helpers import SearchHelper


class IndexerHelper():

    @staticmethod
    def indexer():
        '''
            Index the already added csv/xlsx data resource for column search.
        '''

        AuthHelpers.abort_if_not_admin()

        # empty the index table
        indexTableModel = DataResourceColumnIndex()
        records = indexTableModel.get_all()
        for rec in records:
            rec.delete()
            rec.commit()


        all_datasets = Package.search_by_name('')
        for package in all_datasets:
            if package.state != 'active':
                continue
            
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            for resource in dataset['resources']:
                 if resource['url_type'] == 'upload' and resource['state'] == "active":
                    if SearchHelper.is_csv(resource):
                        dataframe_columns, fit_for_autotag = SearchHelper.get_csv_columns(resource['id'])
                        columns_names = ""
                        for col in dataframe_columns:
                            columns_names += (str(col) + ",")
                        if len(dataframe_columns) != 0:
                            SearchHelper.add_index(resource['id'], columns_names)  
                    
                    elif SearchHelper.is_xlsx(resource):
                        xls_dataframes_columns = SearchHelper.get_xlsx_columns(resource['id'])
                        if len(xls_dataframes_columns) == 0:
                            continue

                        columns_names = ""
                        for sheet, columns_object in xls_dataframes_columns.items():
                            for col in columns_object[0]:  
                                columns_names += (str(col) + ",")
                                
                        SearchHelper.add_index(resource['id'], columns_names)                       
        
        return "Indexed"



    @staticmethod
    def add_index(resource_id, index_value):
        '''
            Index a data resource columns name in the database.
        '''
        
        check_existence_indexer = DataResourceColumnIndex()
        if not check_existence_indexer.get_by_resource(id=resource_id):
            column_indexer = DataResourceColumnIndex(resource_id=resource_id, columns_names=index_value)
            column_indexer.save()
            return True
        
        # first delete all old records and then add
        records = check_existence_indexer.get_by_resource(id=resource_id)
        for rec in records:
            rec.delete()
            rec.commit()
        
        column_indexer = DataResourceColumnIndex(resource_id=resource_id, columns_names=index_value)
        column_indexer.save()
        return True
