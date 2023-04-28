# encoding: utf-8

from ckan.model import Package
from ckanext.crc1153.models.data_resource_column_index import DataResourceColumnIndex
from ckanext.crc1153.libs.auth_helpers import AuthHelpers
from ckanext.crc1153.libs.crc_search.file_helpers import FileHelper


class IndexerHelper():

    @staticmethod
    def indexer():
        '''
            Index the already added csv/xlsx data resource for column search.
        '''

        try:
            AuthHelpers.abort_if_not_admin()
            IndexerHelper.delete_the_old_index()
            all_datasets = Package.search_by_name('')
            for package in all_datasets:
                if package.state != 'active':
                    continue                
                dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
                for resource in dataset['resources']:
                    if resource['url_type'] == 'upload' and resource['state'] == "active":
                        if FileHelper.is_csv(resource):
                            columns_names = IndexerHelper.shape_csv_column_names_for_index(resource['id'])
                            IndexerHelper.add_index(resource['id'], columns_names)
                                                          
                        elif FileHelper.is_xlsx(resource):
                            columns_names = IndexerHelper.shape_xlsx_column_names_for_index(resource['id'])
                            IndexerHelper.add_index(resource['id'], columns_names) 
        except:
            # return "Indexed Failed!"
            raise
        
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



    @staticmethod
    def delete_the_old_index():
         # empty the index table
        indexTableModel = DataResourceColumnIndex()
        records = indexTableModel.get_all()
        for rec in records:
            rec.delete()
            rec.commit()
    

    @staticmethod
    def shape_csv_column_names_for_index(resource_id):
        dataframe_columns, _ = FileHelper.get_csv_columns(resource_id)
        columns_names = ""
        for col in dataframe_columns:
            columns_names += (str(col) + ",")
        return columns_names


    @staticmethod
    def shape_xlsx_column_names_for_index(resource_id):
        xls_dataframes_columns = FileHelper.get_xlsx_columns(resource_id)        
        columns_names = ""
        for sheet, columns_object in xls_dataframes_columns.items():
            for col in columns_object[0]:  
                columns_names += (str(col) + ",")
        return columns_names