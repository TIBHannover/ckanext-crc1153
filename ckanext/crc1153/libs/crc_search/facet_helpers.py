# encoding: utf-8




class FacetHelper():

    @staticmethod
    def update_search_facet_with_dataset(search_facet_object, dataset):
       
        facet_fields = ['sfb_dataset_type', 'organization', 'tags', 'groups']
        for facet_name in facet_fields:
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