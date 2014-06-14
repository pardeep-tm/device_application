#!/usr/bin/python
import sys,os
sys.path.append('/opt/omd/sites/nms1')
import mongo_functions
#arg_list =str(sys.argv)



#with open("/opt/omd/sites/nms1/nt1.log","a") as f1:
#	f1.write("nitin")


file_path = os.path.dirname(os.path.abspath(__file__))
path = [path for path in file_path.split('/')]	

if len(path) <= 4 or 'sites' not in path:
	raise Exception, "Place the file in appropriate omd site"
else:
	site = path[path.index('sites') + 1]

notification_event_dict = {}
db = mongo_functions.mongo_db_conn(site,"nocout_event_log")
notification_event_dict = dict(host_address=sys.argv[1],
		host_name=sys.argv[2],host_state=sys.argv[3],
		time=sys.argv[4])

mongo_functions.mongo_db_insert(db,notification_event_dict,"notification_event")
