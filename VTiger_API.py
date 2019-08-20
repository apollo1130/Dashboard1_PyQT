#https://www.vtiger.com/docs/rest-api-for-vtiger
import requests, json

username ='(USERNAME)'
access_key = '(ACCESS KEY)'
host = 'https://(MYURL).vtiger.com/restapi/v1/vtiger/default'



#Get information about me
#url = f"{host}/me"

#Return information about each of the modules within VTiger
#url = f"{host}/listtypes?fieldTypeList=null"

#Query Case Module and order by Modified Time
#Returns the first 100 cases
#url = f"{host}/query?query=Select * FROM Cases order by modifiedtime;"

#Return the items from the FAQ module
#url = f"{host}/query?query=Select * FROM Faq;"



r = requests.get(url, auth=(username, access_key))

print(f"The status code is: {r.status_code}\n")

#Write JSON data to a file
r_text = json.loads(r.text)
my_data = json.dumps(r_text, indent=4)
with open('dict1.json', 'w') as f:
    f.write(my_data)
