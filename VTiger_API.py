#https://www.vtiger.com/docs/rest-api-for-vtiger
#Get information about me
#url = f"{host}/me"
#
#Return information about each of the modules within VTiger
#url = f"{host}/listtypes?fieldTypeList=null"
#
#Query Case Module for cases that are not resolved or closed
#url = f"{host}/query?query=Select * FROM Cases WHERE casestatus != 'closed' AND casestatus != 'resolved' limit 100,200;"
#
#Returns a count of the items that match the query. In this case, returns the amount of open cases assigned to the user with the '19x62' id.
#>>> r_text
#{'success': True, 'result': [{'count': '229'}]}
#url = f"{host}/query?query=SELECT COUNT(*) FROM Cases WHERE group_id = '20x5' AND casestatus != 'closed' AND casestatus != 'resolved';"
#
#Get information about a module's fields, Cases in this example
#url = f"{host}/describe?elementType=Employees"

import requests, json

username ='(USERNAME)'
access_key = '(ACCESS KEY)'
host = 'https://(MYURL).vtiger.com/restapi/v1/vtiger/default'

def api_call(url, filename):
    '''
    Accepts a URL and returns the text
    '''
    r = requests.get(url, auth=(username, access_key))
    print(f"The status code is: {r.status_code}")
    r_text = json.loads(r.text)
    print("Number of Results: ", len(r_text['result']))    
    #Write to a file for backup/review
    #TODO - Need a better way to write each API call as a separate file
    #Although this won't be necessary long term anyway. It's mainly for testing.
    my_data = json.dumps(r_text, indent=4)
    with open(f"{filename}.json", 'w') as f:
        f.write(my_data)
        
    return r_text

def user_dictionary(host):    
    '''
    Accepts User List and returns a dictionary of the username, first, last and id
    '''
    user_list = api_call(f"{host}/query?query=Select * FROM Users;", 'users')
    
    num_of_users = len(user_list['result'])
    username_list = []
    for user in range(num_of_users):
        username_list.append(user_list['result'][user]['user_name'])
        
    #Creates a dictionary with every username as the key and an empty list as the value
    user_dict = {i : [] for i in username_list}

    #Assigns a list of the first name, last name and User ID to the username
    for username in range(num_of_users): 
        user_dict[username_list[username]] = [user_list['result'][username]['first_name'], user_list['result'][username]['last_name'], user_list['result'][username]['id'], user_list['result'][username]['user_primary_group']]
        
    return user_dict

def group_dictionary(host):    
    '''
    Accepts Group List and returns a dictionary of the Group Name and ID
    '''
    group_list = api_call(f"{host}/query?query=Select * FROM Groups;", 'groups')

    num_of_groups = len(group_list['result'])
    groupname_list = []
    for group in range(num_of_groups):
        groupname_list.append(group_list['result'][group]['groupname'])
        
    #Creates a dictionary with every group name as the key and an empty list as the value
    group_dict = {i : [] for i in groupname_list}

    #Assigns a list of the first name, last name and User ID to the username
    for groupname in range(num_of_groups): 
        group_dict[groupname_list[groupname]] = group_list['result'][groupname]['id']
        
    return group_dict

def case_count(host):
    '''
    Get the amount of cases that aren't closed or resolved and are assigned to the 20x5 group and return the number as an int
    '''
    case_amount = api_call(f"{host}/query?query=SELECT COUNT(*) FROM Cases WHERE group_id = '20x5' AND casestatus != 'closed' AND casestatus != 'resolved';", "casecount")
    num_cases = case_amount['result'][0]['count']
    return num_cases

num_cases = case_count(host)
print(num_cases)

#group_dict = group_dictionary(host)
#user_dict = user_dictionary(host)
#for k, v in group_dict.items():
#    print(f"{k}: {v}")  

