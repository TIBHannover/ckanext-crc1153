# encoding: utf-8

import ckan.plugins.toolkit as toolkit
import clevercsv
import pandas as pd
from ckan.model import Package
import ckan.model as model
import ckan.logic as logic
# from ckanext.sfb_search_extension.models.data_resource_column_index import DataResourceColumnIndex


RESOURCE_DIR = toolkit.config['ckan.storage_path'] + '/resources/'
STANDARD_HEADERS = ['X-Kategorie', 'Y-Kategorie', 'Datentyp', 'Werkstoff-1', 'Werkstoff-2', 'Atmosphaere', 'Vorbehandlung']

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
        # indexTableModel = DataResourceColumnIndex()
        # records = indexTableModel.get_all()
        # for rec in records:
        #     rec.delete()
        #     rec.commit()


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
        
        # check_existence_indexer = DataResourceColumnIndex()
        # if not check_existence_indexer.get_by_resource(id=resource_id):
        #     column_indexer = DataResourceColumnIndex(resource_id=resource_id, columns_names=index_value)
        #     column_indexer.save()
        #     return True
        
        # first delete all old records and then add
        # records = check_existence_indexer.get_by_resource(id=resource_id)
        # for rec in records:
        #     rec.delete()
        #     rec.commit()
        
        # column_indexer = DataResourceColumnIndex(resource_id=resource_id, columns_names=index_value)
        # column_indexer.save()
        return True



    @staticmethod
    def skip_data(resource_id):
        '''
            Skip the resource owner dataset that should not be on the search result.
        '''

        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        resource = ""
        dataset = "" 
        try:
            toolkit.check_access('resource_show', context, {'id':resource_id})
            resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
        except toolkit.NotAuthorized:
            return True

        try:
            toolkit.check_access('package_show', context, {'name_or_id': resource['package_id']})
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': resource['package_id']})
        except toolkit.NotAuthorized:
            return True

        if dataset['state'] != "active":
            return True
        
        return False



    @staticmethod
    def is_possible_to_automate(resource_df):
        '''
            If data file is annotated or not.
        '''

        df_columns = resource_df.columns
        if len(df_columns) != len(STANDARD_HEADERS):
            return False
        for header in df_columns:
            if header.strip() not in STANDARD_HEADERS:
                return False
        return True
    


    @staticmethod
    def add_search_result(dataset, search_filters_string, search_results):
        '''
            Add a dataset to search result based on the search filter.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq]
                - search_result: search result array
        '''

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

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
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

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
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

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
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
    def apply_filters_tags(dataset, search_filters_string):
        '''
            Apply tags facet filters for a dataset.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
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

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
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
    def update_search_facet(search_facet_object, dataset, facet_name):
        '''
            Update the search facet based on the search results.
        '''

        if facet_name == 'organization':
            place = 0
            exist = False
            for item in search_facet_object[facet_name]['items']:
                if dataset[facet_name]['name'] in item.values():
                    search_facet_object[facet_name]['items'][place]['count'] += 1
                    exist = True
                    break
                place += 1
            
            if not exist:
                search_facet_object[facet_name]['items'].append({
                    'name': dataset['organization']['name'], 
                    'display_name': dataset['organization']['title'], 
                    'count': 1
                    }) 
        

        elif facet_name == 'tags':
            for tag in dataset['tags']:
                place = 0
                exist = False
                for item in search_facet_object[facet_name]['items']:
                    if tag['name'] in item.values():
                        search_facet_object[facet_name]['items'][place]['count'] += 1
                        exist = True
                        break
                    place += 1
                
                if not exist:
                    search_facet_object[facet_name]['items'].append({
                        'name': tag['name'], 
                        'display_name': tag['display_name'], 
                        'count': 1
                        }) 

        elif facet_name == 'groups':
            for group in dataset['groups']:
                place = 0
                exist = False
                for item in search_facet_object[facet_name]['items']:
                    if group['name'] in item.values():
                        search_facet_object[facet_name]['items'][place]['count'] += 1
                        exist = True
                        break
                    place += 1
                
                if not exist:
                    search_facet_object[facet_name]['items'].append({
                        'name': group['name'], 
                        'display_name': group['display_name'], 
                        'count': 1
                        }) 
        
        elif facet_name == 'sfb_dataset_type' and 'sfb_dataset_type' in dataset.keys() and facet_name in search_facet_object.keys():
            place = 0
            exist = False
            for item in search_facet_object[facet_name]['items']:
                if dataset[facet_name] in item.values():
                    search_facet_object[facet_name]['items'][place]['count'] += 1
                    exist = True
                    break
                place += 1
            
            if not exist and dataset['sfb_dataset_type'] not in ['', '0']:
                search_facet_object[facet_name]['items'].append({
                    'name': dataset['sfb_dataset_type'], 
                    'display_name': dataset['sfb_dataset_type'], 
                    'count': 1
                    }) 



        return search_facet_object



    @staticmethod
    def is_csv(resource):
        '''
            Check if a data resource in csv or not.

            Args:
                - resource: the data resource object.
            
            Returns:
                - Boolean        
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

            Args:
                - resource_id: the data resource id in ckan
            
            Returns:
                - a list of columns names
        '''

        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        try:
            df = clevercsv.read_dataframe(file_path)
            df = df.fillna(0)        
            if not SearchHelper.is_possible_to_automate(df):
                return [list(df.columns), False]
            else:
                # skip the first row to get the actual columns names
                return [list(df.iloc[0]), True]
        except:
            return[[], False]
    



    @staticmethod
    def is_xlsx(resource):
        '''
            Check if a data resource in xlsx or not.

            Args:
                - resource: the data resource object.
            
            Returns:
                - Boolean        
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
        '''
            Read a xlsx file as pandas dataframe and return the columns name.

            Args:
                - resource_id: the data resource id in ckan
            
            Returns:
                - a list of columns names
        '''

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
                if not SearchHelper.is_possible_to_automate(final_data_df):
                    result_df[sheet] = [final_data_df, False]
                else:
                    result_df[sheet] = [list(final_data_df.iloc[0]), True]

        return result_df



    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins")
        if plugin_name in plugins:
            return True
        return False
    


    def check_access_package(package_id):
        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        data_dict = {'id':package_id}
        try:
            toolkit.check_access('package_show', context, data_dict)
            return True

        except toolkit.NotAuthorized:
            return False
