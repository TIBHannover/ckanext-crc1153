# encoding: utf-8

import logging
import os

import ckan.plugins.toolkit as toolkit
import clevercsv
import pandas as pd


log = logging.getLogger(__name__)


class FileHelper():

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
    def get_csv_columns(resource_id):
        '''
            Read a csv file as pandas dataframe and return the columns name.
        '''

        file_path = FileHelper._resource_path(resource_id)
        try:
            df = clevercsv.read_dataframe(file_path)
            df = df.fillna(0)        
            return [list(df.columns), False]
        except (OSError, UnicodeDecodeError, ValueError) as err:
            log.warning("Could not read CSV resource %s: %s", resource_id, err.__class__.__name__)
            return[[], False]
    


    @staticmethod
    def get_xlsx_columns(resource_id):
        result_df = {}
        file_path = FileHelper._resource_path(resource_id)
        try:
            data_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        except (OSError, ValueError) as err:
            log.warning("Could not read XLSX resource %s: %s", resource_id, err.__class__.__name__)
            return {}

        for sheet, data_f in data_sheets.items():
            temp_df = data_f.dropna(how='all').dropna(how='all', axis=1)
            if len(temp_df) > 0:
                headers = temp_df.iloc[0]
                final_data_df  = pd.DataFrame(temp_df.values[1:], columns=headers)
                result_df[sheet] = [final_data_df, False]

        return result_df

    @staticmethod
    def _resource_path(resource_id):
        resource_dir = os.path.join(
            toolkit.config.get('ckan.storage_path', ''),
            'resources',
        )
        return os.path.join(
            resource_dir,
            resource_id[0:3],
            resource_id[3:6],
            resource_id[6:],
        )
