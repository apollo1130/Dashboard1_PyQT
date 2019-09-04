#https://www.vtiger.com/docs/rest-api-for-vtiger
#Get information about me
#url = f"{host}/me"
#
#Return information about each of the modules within VTiger
#url = f"{host}/listtypes?fieldTypeList=null"
#
#Get information about a module's fields, Cases in this example
#url = f"{host}/describe?elementType=Employees"

import requests, json, datetime

username ='(USERNAME)'
access_key = '(ACCESS KEY)'
host = 'https://(MYURL).vtiger.com/restapi/v1/vtiger/default'

def api_call(url, filename, write_to_file = 'yes', fileaccess = 'w'):
    '''
    Accepts a URL and returns the text
    '''
    r = requests.get(url, auth=(username, access_key))
    #print(f"The status code is: {r.status_code}")
    r_text = json.loads(r.text)
    #print(f"Amount of {filename}: {len(r_text['result'])} \n")    
    #Write to a file for backup/review
    #TODO - Need a better way to write each API call as a separate file
    #Although this won't be necessary long term anyway. It's mainly for testing.
    if write_to_file == 'yes':
        my_data = json.dumps(r_text, indent=4)
        with open(f"{filename}.json", fileaccess) as f:
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


def get_all_open_cases(host):
    '''
    A module can only return a maximum of 100 results. To circumvent that, an offset can be supplied which starts returning data from after the offset.
    The amount must be looped through in order to retrieve all the results.
    For instance if there are 250 cases, first 100 is retrieved, then another 100, and then 50.
    A list is returned of each dictionary that was retrieved this way.
    '''
    num_cases = int(case_count(host))
    case_list = []
    offset = 0
    if num_cases > 100:
        while num_cases > 100:
            cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus != 'resolved' AND casestatus != 'closed' limit {offset}, 100;", "cases", 'no')
            case_list.append(cases['result'])
            offset += 100
            num_cases = num_cases - offset
            if num_cases <= 100:
                break
    if num_cases <= 100:
        cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus != 'resolved' AND casestatus != 'closed' limit {offset}, 100;", "cases", 'no')
        case_list.append(cases['result'])
    
    #Combine the multiple lists of dictionaries into one list
    #Before: [[{case1}, {case2}], [{case 101}, {case 102}]]
    #After: [{case1}, {case2}, {case 101}, {case 102}]
    full_case_list = []
    for caselist in case_list:
        full_case_list += caselist
    return full_case_list


def get_today_closed_cases(host):
    '''
    Returns a list of all the cases that have been closed since the beginning of today.
    '''
    today_closed_case_list = []
    today = datetime.datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'
    cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus = 'resolved' AND sla_actual_closureon >= '{today}' limit 0, 100;", "cases", 'no')
    for case in cases['result']:
        today_closed_case_list.append(case)
    return today_closed_case_list


def get_today_open_cases(host):
    '''
    Returns a list of all the cases that have been closed since the beginning of today.
    '''
    today_open_case_list = []
    today = datetime.datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'
    cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus != 'resolved' AND casestatus != 'closed' AND createdtime >= '{today}' limit 0, 100;", "cases", 'no')
    for case in cases['result']:
        today_open_case_list.append(case)
    return today_open_case_list


def print_stats(host):
    '''
    Prints the total number of open cases,
    How many cases were open today,
    How many cases were closed today.
    '''
    today_open_cases = len(get_today_open_cases(host))
    today_closed_cases = len(get_today_closed_cases(host))
    num_cases_total = case_count(host)

    print("Total Number of Support Group Cases:", num_cases_total)
    print("Today's Opened Cases:", today_open_cases)
    print("Today's Closed Cases:", today_closed_cases)
    print("Today's Kill Ratio is:", "{:.0%}".format(today_closed_cases / today_open_cases))


print_stats(host)
