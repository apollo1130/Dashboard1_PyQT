#https://www.vtiger.com/docs/rest-api-for-vtiger
import requests, json

username ='(USERNAME)'
access_key = '(ACCESS KEY)'
host = 'https://(MYURL).vtiger.com/restapi/v1/vtiger/default'

def get_user_list(host):
    '''
    Retrieve text of all the user list within VTiger
    '''
    url = f"{host}/query?query=Select * FROM Users;"    
    r = requests.get(url, auth=(username, access_key))
    print(f"The status code is: {r.status_code}")
    r_text = json.loads(r.text)
    print("Number of Results: ", len(r_text['result']))    
    #Write to a file for backup/review
    write_to_file(r_text)
    return r_text

def write_to_file(r_text):
    '''
    Write the Text response to a file
    '''
    my_data = json.dumps(r_text, indent=4)
    with open('dict1.json', 'w') as f:
        f.write(my_data)
    return None

def user_dictionary(host):    
    '''
    Accepts User List and returns a dictionary of the username, first, last and id
    '''
    user_list = get_user_list(host)
    num_of_users = len(user_list['result'])
    username_list = []
    for user in range(num_of_users):
        username_list.append(user_list['result'][user]['user_name'])
        
    #Creates a dictionary with every username as the key and an empty list as the value
    user_dict = {i : [] for i in username_list}

    #Assigns a list of the first name, last name and User ID to the username
    for username in range(num_of_users): 
        user_dict[username_list[username]] = [user_list['result'][username]['first_name'], user_list['result'][username]['last_name'], user_list['result'][username]['id']]
        
    return user_dict


user_dict = user_dictionary(host)

for k, v in user_dict.items():
    print(k, v)


   
#Get information about me
#url = f"{host}/me"

#Return information about each of the modules within VTiger
#url = f"{host}/listtypes?fieldTypeList=null"

#Query Case Module for cases that are not resolved or closed
#url = f"{host}/query?query=Select * FROM Cases WHERE casestatus != 'closed' AND casestatus != 'resolved' limit 100,200;"

#Returns a count of the items that match the query. In this case, returns the amount of open cases assigned to the user with the '19x62' id.
#>>> r_text
#{'success': True, 'result': [{'count': '229'}]}
#url = f"{host}/query?query=SELECT COUNT(*) FROM Cases WHERE assigned_user_id = '19x62' AND casestatus != 'closed' AND casestatus != 'resolved';"

#Get information about a module's fields, Cases in this example
#url = f"{host}/describe?elementType=Employees"
