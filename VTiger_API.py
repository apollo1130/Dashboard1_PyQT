#https://www.vtiger.com/docs/rest-api-for-vtiger
#Get information about me
#url = f"{host}/me"
#
#Return information about each of the modules within VTiger
#url = f"{host}/listtypes?fieldTypeList=null"
#
#Get information about a module's fields, Cases in this example
#url = f"{host}/describe?elementType=Employees"

import requests, json, datetime, collections, time

class Vtiger_api:
    def __init__(self, username, access_key, host):

        self.username = username
        self.access_key = access_key
        self.host = host

        self.full_user_dict = {}

        self.today_open_case_list = []
        self.today_closed_case_list = []
        self.week_open_case_list = []
        self.week_closed_case_list = []

        self.seconds_to_wait = 0
        

    def api_call(self, url):
        '''
        Accepts a URL and returns the text
        '''
        r = requests.get(url, auth=(self.username, self.access_key))
        header_dict = r.headers

        #We're only allowed 60 API requests per minute. 
        #When we are close to reaching this limit,
        #We pause for the remaining time until it resets.
        if int(header_dict['X-FloodControl-Remaining']) <= 5:
            self.seconds_to_wait = abs(int(header_dict['X-FloodControl-Reset']) - int(time.time()))
            time.sleep(self.seconds_to_wait)
            self.seconds_to_wait = 0
        r_text = json.loads(r.text)
        return r_text


    def get_users(self):    
        '''
        Accepts User List and returns a dictionary of the username, first, last and id
        '''
        user_list = self.api_call(f"{self.host}/query?query=Select * FROM Users;")
        
        num_of_users = len(user_list['result'])
        username_list = []
        for user in range(num_of_users):
            username_list.append(user_list['result'][user]['id'])
            
        #Creates a dictionary with every username as the key and an empty list as the value
        user_dict = {i : [] for i in username_list}

        #Assigns a list of the first name, last name and User ID to the username
        for username in range(num_of_users): 
            user_dict[username_list[username]] = [user_list['result'][username]['first_name'], user_list['result'][username]['last_name'], user_list['result'][username]['user_name'], user_list['result'][username]['user_primary_group']]       
        
        self.full_user_dict = user_dict
        return user_dict


    def get_groups(self):    
        '''
        Accepts Group List and returns a dictionary of the Group Name and ID
        '''
        group_list = self.api_call(f"{self.host}/query?query=Select * FROM Groups;")

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


    def case_count(self, group_id):
        '''
        Get the amount of cases that aren't closed or resolved and are assigned to the supplied group and return the number as an int
        '''
        case_amount = self.api_call(f"{self.host}/query?query=SELECT COUNT(*) FROM Cases WHERE group_id = {group_id} AND casestatus != 'closed' AND casestatus != 'resolved';")
        num_cases = case_amount['result'][0]['count']
        return num_cases


    def get_all_open_cases(self, group_id):
        '''
        A module can only return a maximum of 100 results. To circumvent that, an offset can be supplied which starts returning data from after the offset.
        The amount must be looped through in order to retrieve all the results.
        For instance if there are 250 cases, first 100 is retrieved, then another 100, and then 50.
        A list is returned of each dictionary that was retrieved this way.
        '''
        num_cases = int(self.case_count())
        case_list = []
        offset = 0
        if num_cases > 100:
            while num_cases > 100:
                cases = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE group_id = {group_id} AND casestatus != 'resolved' AND casestatus != 'closed' limit {offset}, 100;")
                case_list.append(cases['result'])
                offset += 100
                num_cases = num_cases - offset
                if num_cases <= 100:
                    break
        if num_cases <= 100:
            cases = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE group_id = {group_id} AND casestatus != 'resolved' AND casestatus != 'closed' limit {offset}, 100;")
            case_list.append(cases['result'])
        
        #Combine the multiple lists of dictionaries into one list
        #Before: [[{case1}, {case2}], [{case 101}, {case 102}]]
        #After: [{case1}, {case2}, {case 101}, {case 102}]
        full_case_list = []
        for caselist in case_list:
            full_case_list += caselist
        return full_case_list


    def beginning_of_week(self):
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


    def get_weeks_closed_cases(self, group_id):
        '''
        Returns a list of all the cases that have been closed since the beginning of today.
        '''

        monday = self.beginning_of_week()
        cases = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE group_id = {group_id} AND casestatus = 'resolved' AND sla_actual_closureon >= '{monday}' limit 0, 100;")
        self.week_closed_case_list = []
        for case in cases['result']:
            self.week_closed_case_list.append(case)
        return self.week_closed_case_list


    def get_weeks_open_cases(self, group_id):
        '''
        Returns a list of all the cases that have been closed since the beginning of today.
        '''
        monday = self.beginning_of_week()
        cases = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE group_id = {group_id} AND createdtime >= '{monday}' limit 0, 100;")

        self.week_open_case_list = []
        for case in cases['result']:
            self.week_open_case_list.append(case)
        return self.week_open_case_list


    def get_today_closed_cases(self, group_id):
        '''
        Returns a list of all the cases that have been closed since the beginning of today.
        '''
        today = datetime.datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'
        cases = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE group_id = {group_id} AND casestatus = 'resolved' AND sla_actual_closureon >= '{today}' limit 0, 100;")
        self.today_closed_case_list = []
        for case in cases['result']:
            self.today_closed_case_list.append(case)
        return self.today_closed_case_list


    def get_today_open_cases(self, group_id):
        '''
        Returns a list of all the cases that have been closed since the beginning of today.
        '''
        today = datetime.datetime.now().strftime("%Y-%m-%d") + ' 00:00:00'
        cases = self.api_call(f"{self.host}/query?query=Select * FROM Cases WHERE group_id = {group_id} AND createdtime >= '{today}' limit 0, 100;")

        self.today_open_case_list = []
        for case in cases['result']:
            self.today_open_case_list.append(case)
        return self.today_open_case_list


    def get_weeks_case_data(self, group_id):
        '''
        Returns the amount of opened and closed cases for the week.
        Also returns the weekly kill ratio.
        '''
        weeks_open_cases = len(self.get_weeks_open_cases(group_id))
        weeks_closed_cases = len(self.get_weeks_closed_cases(group_id))
        if weeks_open_cases == 0:
            week_kill_ratio = str(weeks_closed_cases) + "00%"
        elif weeks_closed_cases == 0:
            week_kill_ratio = "0%"
        else:
            week_kill_ratio = "{:.0%}".format(weeks_closed_cases/ weeks_open_cases)
        
        return weeks_open_cases, weeks_closed_cases, week_kill_ratio
   

    def get_today_case_data(self, group_id):
        '''
        Returns the amount of opened and closed cases for today.
        Also returns the daily kill ratio.
        '''
        today_open_cases = len(self.get_today_open_cases(group_id))
        today_closed_cases = len(self.get_today_closed_cases(group_id))
        if today_open_cases == 0:
            today_kill_ratio = str(today_closed_cases) + "00%"
        elif today_closed_cases == 0:
            today_kill_ratio = "0%"
        else:
            today_kill_ratio = "{:.0%}".format(today_closed_cases / today_open_cases)
        
        return today_open_cases, today_closed_cases, today_kill_ratio

    def week_user_stats(self):
        '''
        Returns an ordered list of tuples with each user ID 
        and the amount of cases they closed this week.
        '''
        if self.full_user_dict == {}:
            self.get_users()
        #Each user_id with a starting amount of 0
        newdict = {i:0 for i in self.full_user_dict}

        #Increment each user ID's value by 1 for each closed case
        for case in self.week_closed_case_list:
            if case['assigned_user_id'] in newdict:
                id = case['assigned_user_id']
                newdict[id] += 1

        #Takes the Dict and sorts it as a list of tuples in descening order
        sorted_user_list = sorted(newdict.items(), key=lambda x: x[1], reverse=True)

        return sorted_user_list

    def today_user_stats(self):
        '''
        Returns an ordered list of tuples with each user ID 
        and the amount of cases they closed this week.
        '''
        if self.full_user_dict == {}:
            self.get_users()
        #Each user_id with a starting amount of 0
        newdict = {i:0 for i in self.full_user_dict}

        #Increment each user ID's value by 1 for each closed case
        for case in self.today_closed_case_list:
            if case['assigned_user_id'] in newdict:
                id = case['assigned_user_id']
                newdict[id] += 1

        #Takes the Dict and sorts it as a list of tuples in descening order
        sorted_user_list = sorted(newdict.items(), key=lambda x: x[1], reverse=True)

        return sorted_user_list

if __name__ == '__main__':
        with open('credentials.json') as f:
            data = f.read()
        credential_dict = json.loads(data)
        vtigerapi = Vtiger_api(credential_dict['username'], credential_dict['access_key'], credential_dict['host'])
        groups = vtigerapi.get_groups()
        print(groups)

