#https://www.vtiger.com/docs/rest-api-for-vtiger
#Get information about me
#url = f"{host}/me"
#
#Return information about each of the modules within VTiger
#url = f"{host}/listtypes?fieldTypeList=null"
#
#Get information about a module's fields, Cases in this example
#url = f"{host}/describe?elementType=Employees"

import requests, json, datetime, collections

username ='(USERNAME)'
access_key = '(ACCESS KEY)'
host = 'https://(MYURL).vtiger.com/restapi/v1/vtiger/default'


def api_call(url):
    '''
    Accepts a URL and returns the text
    '''
    r = requests.get(url, auth=(username, access_key))
    #print(f"The status code is: {r.status_code}")
    r_text = json.loads(r.text)
    return r_text


def get_users(host):    
    '''
    Accepts User List and returns a dictionary of the username, first, last and id
    '''
    user_list = api_call(f"{host}/query?query=Select * FROM Users;")
    
    num_of_users = len(user_list['result'])
    username_list = []
    for user in range(num_of_users):
        username_list.append(user_list['result'][user]['id'])
        
    #Creates a dictionary with every username as the key and an empty list as the value
    user_dict = {i : [] for i in username_list}

    #Assigns a list of the first name, last name and User ID to the username
    for username in range(num_of_users): 
        user_dict[username_list[username]] = [user_list['result'][username]['first_name'], user_list['result'][username]['last_name'], user_list['result'][username]['user_name'], user_list['result'][username]['user_primary_group']]       
    return user_dict


def get_groups(host):    
    '''
    Accepts Group List and returns a dictionary of the Group Name and ID
    '''
    group_list = api_call(f"{host}/query?query=Select * FROM Groups;")

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
    case_amount = api_call(f"{host}/query?query=SELECT COUNT(*) FROM Cases WHERE group_id = '20x5' AND casestatus != 'closed' AND casestatus != 'resolved';")
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
            cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus != 'resolved' AND casestatus != 'closed' limit {offset}, 100;")
            case_list.append(cases['result'])
            offset += 100
            num_cases = num_cases - offset
            if num_cases <= 100:
                break
    if num_cases <= 100:
        cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus != 'resolved' AND casestatus != 'closed' limit {offset}, 100;")
        case_list.append(cases['result'])
    
    #Combine the multiple lists of dictionaries into one list
    #Before: [[{case1}, {case2}], [{case 101}, {case 102}]]
    #After: [{case1}, {case2}, {case 101}, {case 102}]
    full_case_list = []
    for caselist in case_list:
        full_case_list += caselist
    return full_case_list


def beginning_of_week():
    '''
    For whichever day of the week it is, this past Monday at 12:00am is returned.
    Today = datetime.datetime(2019, 9, 5, 15, 31, 13, 134153)
    Returns: 2019-09-02 00:00:00
    '''
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    #0 = monday, 5 = Saturday, 6 = Sunday 
    day = today.weekday()
    today = today + datetime.timedelta(days = -day)   
    return today


def get_weeks_closed_cases(host):
    '''
    Returns a list of all the cases that have been closed since the beginning of today.
    '''
    week_closed_case_list = []
    monday = beginning_of_week()
    cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus = 'resolved' AND sla_actual_closureon >= '{monday}' limit 0, 100;")
    for case in cases['result']:
        week_closed_case_list.append(case)
    return week_closed_case_list

def get_weeks_open_cases(host):
    '''
    Returns a list of all the cases that have been closed since the beginning of today.
    '''
    week_open_case_list = []
    monday = beginning_of_week()
    cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus != 'resolved' AND casestatus != 'closed' AND createdtime >= '{monday}' limit 0, 100;")
    for case in cases['result']:
        week_open_case_list.append(case)
    return week_open_case_list


def get_today_closed_cases(host):
    '''
    Returns a list of all the cases that have been closed since the beginning of today.
    '''
    today_closed_case_list = []
    today = datetime.datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'
    cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus = 'resolved' AND sla_actual_closureon >= '{today}' limit 0, 100;")
    for case in cases['result']:
        today_closed_case_list.append(case)
    return today_closed_case_list


def get_today_open_cases(host):
    '''
    Returns a list of all the cases that have been closed since the beginning of today.
    '''
    today_open_case_list = []
    today = datetime.datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'
    cases = api_call(f"{host}/query?query=Select * FROM Cases WHERE group_id = '20x5' AND casestatus != 'resolved' AND casestatus != 'closed' AND createdtime >= '{today}' limit 0, 100;")
    for case in cases['result']:
        today_open_case_list.append(case)
    return today_open_case_list


def print_stats(host):
    '''
    Outputs the following as an example:

    Total Number of Open Support Group Cases: 131

    Total Cases opened this week: 9
    Total Cases closed this week: 24
    This Week's Kill Ratio is: 267%

    Cases closed this week: 
    James Johnson: 8
    Kurt Biscuit: 8
    Allen Key: 7
    Ariel Fishberg: 1


    Today's Opened Cases: 3
    Today's Closed Cases: 11
    Today's Kill Ratio is: 367%

    Cases closed today: 
    Kurt Biscuit: 6
    Allen Key: 3
    James Johnson: 2
    
    '''
    today_open_cases = len(get_today_open_cases(host))
    today_closed_cases = get_today_closed_cases(host)
    num_cases_total = case_count(host)
    weeks_closed_cases = get_weeks_closed_cases(host)
    weeks_open_cases = get_weeks_open_cases(host)
    

    print("Total Number of Open Support Group Cases:", num_cases_total)
    print()
    print("Total Cases opened this week:", len(weeks_open_cases))
    print("Total Cases closed this week:", len(weeks_closed_cases))
    print("This Week's Kill Ratio is:", "{:.0%}".format(len(weeks_closed_cases) / len(weeks_open_cases)))
    print()

    users = get_users(host)
    #Each user_id with a starting amount of 0
    newdict = {i:0 for i in users}

    #Increment each user ID's value by 1 for each closed case
    for case in weeks_closed_cases:
        if case['assigned_user_id'] in newdict:
            id = case['assigned_user_id']
            newdict[id] += 1

    #Takes the Dict and sorts it as a list of tuples in descening order
    sorted_dict = sorted(newdict.items(), key=lambda x: x[1], reverse=True)

    
    #Print each user's amount of closed cases this past week
    print("Cases closed this week: ")
    for item in range(len(sorted_dict)):
        if sorted_dict[item][1] > 0:
            print(f"{users[sorted_dict[item][0]][0]} {users[sorted_dict[item][0]][1]}: {sorted_dict[item][1]}")

    print("\n\nToday's Opened Cases:", today_open_cases)
    print("Today's Closed Cases:", len(today_closed_cases))
    print("Today's Kill Ratio is:", "{:.0%}".format(len(today_closed_cases) / today_open_cases))
    print()
    print("Cases closed today: ")
    newdict = {i:0 for i in users}

    #Increment each user ID's value by 1 for each closed case
    for case in today_closed_cases:
        if case['assigned_user_id'] in newdict:
            id = case['assigned_user_id']
            newdict[id] += 1
            
    #Takes the Dict and sorts it as a list of tuples in descening order
    sorted_dict = sorted(newdict.items(), key=lambda x: x[1], reverse=True)
    
    #Print each user's amount of closed cases today
    for item in range(len(sorted_dict)):
        if sorted_dict[item][1] > 0:
            print(f"{users[sorted_dict[item][0]][0]} {users[sorted_dict[item][0]][1]}: {sorted_dict[item][1]}")


print_stats(host)

