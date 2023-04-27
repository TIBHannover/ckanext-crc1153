# encoding: utf-8




class FacetHelper():

    @staticmethod
    def update_search_facet_with_dataset(search_facet_object, dataset):               
        search_facet_object = FacetHelper.add_dataset_organization_to_facet(search_facet_object, dataset)
        search_facet_object = FacetHelper.add_dataset_tags_to_facet(search_facet_object, dataset)
        search_facet_object = FacetHelper.add_dataset_groups_to_facet(search_facet_object, dataset)        
        if 'sfb_dataset_type' in dataset.keys() and 'sfb_dataset_type' in search_facet_object.keys():
            search_facet_object = FacetHelper.add_dataset_type_to_facet(search_facet_object, dataset)
                
        return search_facet_object
    

    @staticmethod
    def add_dataset_organization_to_facet(search_facet_object, dataset):
        index = 0
        exist = False
        for item in search_facet_object['organization']['items']:
            if dataset['organization']['name'] in item.values():
                search_facet_object['organization']['items'][index]['count'] += 1
                exist = True
                break
            index += 1
        
        if not exist:            
            search_facet_object['organization']['items'].append({'name': dataset['organization']['name'], 'display_name': dataset['organization']['title'], 'count': 1})
        return search_facet_object



    @staticmethod
    def add_dataset_tags_to_facet(search_facet_object, dataset):
        for tag in dataset['tags']:                    
            place = 0
            exist = False
            for item in search_facet_object['tags']['items']:
                if tag['name'] in item.values():
                    search_facet_object['tags']['items'][place]['count'] += 1
                    exist = True
                    break
                place += 1
            
            if not exist:
                search_facet_object['tags']['items'].append({'name': tag['name'], 'display_name': tag['display_name'], 'count': 1}) 
            
        return search_facet_object
    


    @staticmethod
    def add_dataset_groups_to_facet(search_facet_object, dataset):
        for group in dataset['groups']:
            place = 0
            exist = False
            for item in search_facet_object['groups']['items']:
                if group['name'] in item.values():
                    search_facet_object['groups']['items'][place]['count'] += 1
                    exist = True
                    break
                place += 1
            
            if not exist:
                search_facet_object['groups']['items'].append({'name': group['name'], 'display_name': group['display_name'], 'count': 1}) 
            
        return search_facet_object


    @staticmethod
    def add_dataset_type_to_facet(search_facet_object, dataset):
        place = 0
        exist = False
        for item in search_facet_object['sfb_dataset_type']['items']:
            if dataset['sfb_dataset_type'] in item.values():
                search_facet_object['sfb_dataset_type']['items'][place]['count'] += 1
                exist = True
                break
            place += 1
        
        if not exist and dataset['sfb_dataset_type'] not in ['', '0']:
            search_facet_object['sfb_dataset_type']['items'].append({'name': dataset['sfb_dataset_type'], 'display_name': dataset['sfb_dataset_type'], 'count': 1}) 
        
        return search_facet_object
    