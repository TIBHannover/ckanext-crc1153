# encoding: utf-8

import ckan.plugins.toolkit as toolkit
import clevercsv
import pandas as pd
from ckan.model import Package
import ckan.model as model
import ckan.logic as logic
from ckanext.crc1153.models.data_resource_column_index import DataResourceColumnIndex
from ckanext.crc1153.libs.auth_helpers import AuthHelpers


RESOURCE_DIR = toolkit.config['ckan.storage_path'] + '/resources/'

class SearchHelper():

    @staticmethod
    def indexer():
        '''
            Index the already added csv/xlsx data resource for column search.
        '''

        context = {'model': model, 'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        try:
            logic.check_access('sysadmin', context, {})
        except logic.NotAuthorized:
            toolkit.abort(404, 'Not found')

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



    @staticmethod
    def skip_if_not_authorized(resource_id):     
        if not AuthHelpers.check_access_show_resource(resource_id):
            return True

        resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
        if not AuthHelpers.check_access_show_package(resource['package_id']):
            return True            
        
        dataset = toolkit.get_action('package_show')({}, {'id': resource['package_id']})
        if dataset['state'] != "active":
            return True
        
        return False


    @staticmethod
    def add_dataset_to_search_result(dataset, search_filters_string, search_results):
        org_filter = SearchHelper.apply_filters_organization(dataset, search_filters_string)
        tag_filter = SearchHelper.apply_filters_tags(dataset, search_filters_string)
        group_filter = SearchHelper.apply_filters_groups(dataset, search_filters_string)
        type_filter = SearchHelper.apply_filters_type(dataset, search_filters_string)

        if org_filter and type_filter and tag_filter and group_filter:
            search_results['results'].append(dataset)
            search_results['count'] = int(search_results['count']) + 1 
    
        return search_results



    @staticmethod
    def apply_filters_organization(dataset, search_filters_string):
        '''
            Apply organization facet filters for a dataset.
        '''

        if len(search_filters_string.split('organization:')) == 2:
            org_name =  search_filters_string.split('organization:"')[1].split('"')[0].strip()
            if dataset['organization']['name']  != org_name:
                return False
        
        elif 'organization:' in search_filters_string:            
                 return False
        
        else:
            return True
        
        return True



    @staticmethod
    def apply_filters_type(dataset, search_filters_string):
        '''
            Apply dataset type facet filters for a dataset.
        '''
       
        if 'sfb_dataset_type' in dataset.keys() and len(search_filters_string.split('sfb_dataset_type:')) == 2:
            dataset_type = search_filters_string.split('sfb_dataset_type:"')[1].split('"')[0].strip()
            if  dataset['sfb_dataset_type']  != dataset_type:
               return False
        
        elif 'sfb_dataset_type:' in search_filters_string:
            return False
        
        else:
            return True
        
        return True
    


    @staticmethod
    def apply_filters_tags(dataset, search_filters_string):
        '''
            Apply tags facet filters for a dataset.
        '''

        if 'tags:' not in search_filters_string:
            return True
        
        for tag in dataset['tags']:
            tag_query = 'tags:"' + tag['name'] + '"'
            if tag_query in search_filters_string:
                search_filters_string = search_filters_string.replace(tag_query, ' ')
        
        if 'tags:' in search_filters_string:
            return False

        return True 
    


    @staticmethod
    def apply_filters_groups(dataset, search_filters_string):
        '''
            Apply groups facet filters for a dataset.
        '''

        if 'groups:' not in search_filters_string:
            return True
        
        for group in dataset['groups']:
            group_query = 'groups:"' + group['name'] + '"'
            if group_query in search_filters_string:
                search_filters_string = search_filters_string.replace(group_query, ' ')
        
        if 'groups:' in search_filters_string:
            return False

        return True 



    @staticmethod
    def is_csv(resource):
        '''
            Check if a data resource in csv or not.       
        '''

        format = ''
        name = ''
        if isinstance(resource, dict):
            format = resource.get('format')
            name = resource.get('name')
        else:
            format = resource.format
            name = resource.name
        
        if not format:
            return False
        
        return (format in ['CSV']) or ('.csv' in name)
    


    @staticmethod
    def get_csv_columns(resource_id):
        '''
            Read a csv file as pandas dataframe and return the columns name.
        '''

        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        try:
            df = clevercsv.read_dataframe(file_path)
            df = df.fillna(0)        
            return [list(df.columns), False]
        except:
            return[[], False]
    



    @staticmethod
    def is_xlsx(resource):
        '''
            Check if a data resource in xlsx or not.      
        '''

        format = ''
        name = ''
        if isinstance(resource, dict):
            format = resource.get('format')
            name = resource.get('name')
        else:
            format = resource.format
            name = resource.name
        
        if not format:
            return False

        return (format in ['XLSX']) or ('.xlsx' in name)



    @staticmethod
    def get_xlsx_columns(resource_id):
        result_df = {}
        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        try:
            data_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        except:
            return {}

        for sheet, data_f in data_sheets.items():
            temp_df = data_f.dropna(how='all').dropna(how='all', axis=1)
            if len(temp_df) > 0:
                headers = temp_df.iloc[0]
                final_data_df  = pd.DataFrame(temp_df.values[1:], columns=headers)
                result_df[sheet] = [final_data_df, False]

        return result_df



    @staticmethod
    def empty_ckan_search_result(search_results_dict, search_params):
        search_results_dict['results'] = []
        search_results_dict['search_facets']['organization']['items'] = []
        search_results_dict['search_facets']['tags']['items'] = []
        search_results_dict['search_facets']['groups']['items'] = []
        if(search_results_dict['search_facets'].get('sfb_dataset_type')):
            search_results_dict['search_facets']['sfb_dataset_type']['items'] = []
        search_results_dict['count'] = 0
        search_results_dict['detected_resources_ids'] = []
        search_filters = search_params['fq'][0]
        return [search_results_dict, search_filters]
    


    @staticmethod
    def dataset_is_not_in_selected_organization(search_filters, dataset_owner_org_id):
        if 'owner_org' in search_filters:
            owner_org_id = search_filters.split('owner_org:')[1]
            if ' ' in owner_org_id:
                owner_org_id = owner_org_id.split(' ')[0]                    
            if '"' + dataset_owner_org_id + '"' != owner_org_id:
                return True
        return False


    @staticmethod
    def dataset_is_not_in_selected_group(search_filters, dataset_groups):
        if 'groups' in search_filters:                          
            target_group_title = search_filters.split('groups:')[1]                                      
            if ' ' in target_group_title:
                target_group_title = target_group_title.split(' ')[0]
            is_part_of_group = False
            for g in dataset_groups:
                group_name = ""
                if type(g) == dict:
                    group_name = g['name']
                else:
                    group_name = g.name                     
                if '"' + group_name + '"' == target_group_title:
                    is_part_of_group = True
                    break
            return not is_part_of_group
        return False
