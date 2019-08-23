#https://www.vtiger.com/docs/rest-api-for-vtiger
import requests, json

username ='(USERNAME)'
access_key = '(ACCESS KEY)'
host = 'https://(MYURL).vtiger.com/restapi/v1/vtiger/default'


#Get information about me
#url = f"{host}/me"

#Return information about each of the modules within VTiger
#url = f"{host}/listtypes?fieldTypeList=null"

#Query Case Module for cases that are not resolved or closed
#url = f"{host}/query?query=Select * FROM Cases WHERE casestatus != 'closed' AND casestatus != 'resolved' limit 100,200;"

#Returns a count of the items that match the query. In this case, returns the amount of open cases assigned to the group with the '20x68' group.
#>>> r_text
#{'success': True, 'result': [{'count': '229'}]}
#url = f"{host}/query?query=SELECT COUNT(*) FROM Cases WHERE group_id = '20x68' AND casestatus != 'closed' AND casestatus != 'resolved';"

#Get information about a module's fields, Cases in this example
#url = f"{host}/describe?elementType=Employees"

#Return the items from the Users module
#Use this and GROUPS to get User and Group IDs
#url = f"{host}/query?query=Select * FROM Users;"

r = requests.get(url, auth=(username, access_key))

print(f"The status code is: {r.status_code}\n")

#Write JSON data to a file
r_text = json.loads(r.text)
my_data = json.dumps(r_text, indent=4)
with open('dict1.json', 'w') as f:
    f.write(my_data)
