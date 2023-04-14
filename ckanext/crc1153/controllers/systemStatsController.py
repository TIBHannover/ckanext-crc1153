# encoding: utf-8

def check_plugin_enabled(plugin_name):
    plugins = toolkit.config.get("ckan.plugins")
    if plugin_name in plugins:
        return True
    return False



from flask import render_template
import ckan.plugins.toolkit as toolkit
from sqlalchemy.sql.expression import false
import ckan.lib.helpers as h
import ckan.model as model
import ckan.logic as logic
from ckan.model import Package, Group, User
if check_plugin_enabled("semantic_media_wiki"):
    from ckanext.semantic_media_wiki.libs.media_wiki import Helper as machineHelper

if check_plugin_enabled("sample_link"):
    from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper

if check_plugin_enabled("dataset_reference"):
    from ckanext.dataset_reference.models.package_reference_link import PackageReferenceLink
 


class BaseController():

    def index():
        context = {'model': model,
                   'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        try:
            logic.check_access('sysadmin', context, {})
        except logic.NotAuthorized:
            toolkit.abort(403, 'Need to be system administrator to administer')

        result = {}
        result['Number of Datasets'] = BaseController.get_dataset_count()
        result['Number of Organizations'], result['Number of Groups'] = BaseController.get_org_group_count()
        result['Number of Users'] = BaseController.get_user_count()
        result['Number of machines resource'], result['Number of machines dataset'] = BaseController.get_linked_machines_count()
        result['Number of samples resource'], result['Number of samples dataset'] = BaseController.get_linked_samples_count()
        result['Number of datasets linked to publication']  = BaseController.get_linked_publications_count()
        result['dataset_per_org'] = BaseController.get_dataset_per_org()
        result['dataset_per_group'] = BaseController.get_dataset_per_group()
        result['resource_per_type'] = BaseController.get_resources_by_type()
        result['datasets_with_publication'] = BaseController.get_dataset_with_publication()
        result['datasets_with_machines'] = BaseController.get_dataset_with_machines()
        result['datasets_with_samples'] = BaseController.get_dataset_with_samples()
        result['datasets_with_annotaion'] = BaseController.get_datasets_with_extra_annotaion()
        result['group_with_datasets_with_publication'] = BaseController.get_dataset_with_publication_per_group()

        return render_template('stats_page.html', result=result)
    


    @staticmethod
    def get_dataset_count():
        count = 0
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            if dataset.state == 'active':
                count += 1
        return count
    


    @staticmethod
    def get_org_group_count():
        org_count = 0
        group_count = 0
        all_groups = Group.all()
        for g in all_groups:
            if g.state != 'active':
                continue
            elif g.is_organization:
                org_count += 1
            else:
                group_count += 1
        
        return [org_count, group_count]
    


    @staticmethod
    def get_user_count():
        count = 0
        all_users = User.all()
        for user in all_users:
            if user.state == 'active' and not user.sysadmin:
                count += 1
        return count
    


    @staticmethod
    def get_linked_machines_count():
        if not check_plugin_enabled("semantic_media_wiki"):
            return [0, 0]
        count = 0
        dataset_count = 0
        dataset_found = False
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            dataset_found = False
            if dataset.state == 'active':
                for res in dataset.resources:
                    if res.state == 'active':
                        links = machineHelper.get_machine_link(res.id)
                        if len(links.keys()) != 0:
                            count += 1
                            if not dataset_found:
                                dataset_count += 1
                                dataset_found = True
        return [count, dataset_count]



    @staticmethod
    def get_linked_samples_count():
        if not check_plugin_enabled("sample_link"):
            return [0,0]
        count = 0
        dataset_count = 0
        dataset_found = False
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            dataset_found = False
            if dataset.state == 'active':
                for res in dataset.resources:
                    if res.state == 'active':
                        links = SampleLinkHelper.get_sample_link(res.id)
                        if len(links.keys()) != 0:
                            count += 1
                            if not dataset_found:
                                dataset_count += 1
                                dataset_found = True
        return [count, dataset_count]
    


    @staticmethod
    def get_linked_publications_count():
        if not check_plugin_enabled("dataset_reference"):
            return 0
        count = 0
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            if dataset.state == 'active':
                res_object = PackageReferenceLink({})
                result = res_object.get_by_package(name=dataset.name)
                if result != false and len(result) != 0:
                    count += 1
        
        return count
    

    @staticmethod
    def get_dataset_per_org():
        org_dataset = {}
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            if dataset.state == 'active':
                org = Group.get(dataset.owner_org)
                if org.title in org_dataset.keys():
                    org_dataset[org.title] += 1
                else:
                    org_dataset[org.title] = 1

        return org_dataset
    


    @staticmethod
    def get_dataset_per_group():
        group_dataset = {}
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            if dataset.state == 'active':
                groups = dataset.get_groups()
                for g in groups:
                    if g.state == 'active' and not g.is_organization:
                        if g.title in group_dataset.keys():
                            group_dataset[g.title] += 1
                        else:
                            group_dataset[g.title] = 1


        return group_dataset
    


    @staticmethod
    def get_resources_by_type():
        resources = {}
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            if dataset.state == 'active':
                for res in dataset.resources:
                    if res.state == 'active':
                        if res.format and res.format != '':
                            if res.format.lower() in resources.keys():
                                resources[res.format.lower()] += 1
                            else:
                                resources[res.format.lower()] = 1

        return resources
    


    @staticmethod
    def get_dataset_with_publication():
        if not check_plugin_enabled("dataset_reference"):
            return []
        result_datasets = []
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            if dataset.state == 'active':
                res_object = PackageReferenceLink({})
                result = res_object.get_by_package(name=dataset.name)
                if result != false and len(result) != 0:
                    result_datasets.append(dataset.title)
        
        return result_datasets


    @staticmethod
    def get_dataset_with_machines():
        if not check_plugin_enabled("semantic_media_wiki"):
            return []
        result_datasets = []
        dataset_found = False
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            dataset_found = False
            if dataset.state == 'active':
                for res in dataset.resources:
                    if res.state == 'active':
                        links = machineHelper.get_machine_link(res.id)
                        if len(links.keys()) != 0:                            
                            if not dataset_found:
                                result_datasets.append(dataset.title)
                                dataset_found = True
                                break
        return result_datasets
    


    @staticmethod
    def get_dataset_with_samples():
        if not check_plugin_enabled("sample_link"):
            return []
        result_datasets = []
        dataset_found = False
        all_datasets = Package.search_by_name('')
        for dataset in all_datasets:
            dataset_found = False
            if dataset.state == 'active':
                for res in dataset.resources:
                    if res.state == 'active':
                        links = SampleLinkHelper.get_sample_link(res.id)
                        if len(links.keys()) != 0:
                            if not dataset_found:
                                result_datasets.append(dataset.title)
                                dataset_found = True
                                break
        return result_datasets
    


    @staticmethod
    def get_datasets_with_extra_annotaion():
        result_datasets = []
        packages = Package.search_by_name('')
        for dataset in packages:
            if dataset.state == 'active':
                dataset_extras = dataset.as_dict()['extras']
                if len(dataset_extras.keys()) == 0:
                    continue
                elif len(dataset_extras.keys()) == 1 and list(dataset_extras.keys())[0] == 'sfb_dataset_type':
                    continue
                else:
                    result_datasets.append(dataset.title)
                                
        return result_datasets



    @staticmethod
    def get_dataset_with_publication_per_group():
        result_groups = {}
        packages = Package.search_by_name('')
        for dataset in packages:
            if dataset.state == 'active':
                res_object = PackageReferenceLink({})
                result = res_object.get_by_package(name=dataset.name)
                if result != false and len(result) != 0:
                    groups = dataset.get_groups()
                    for g in groups:
                        if g.state == 'active' and not g.is_organization:
                            if g.title in result_groups.keys():
                                result_groups[g.title].append(dataset.title)
                            else:
                                result_groups[g.title] = [dataset.title]

        return result_groups