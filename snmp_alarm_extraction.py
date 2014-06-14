import mysql_functions,mongo_functions
import json ,rrd_main
import socket,os
from datetime import datetime, timedelta
def snmp_alarm_extraction():
        try:
                query = "GET hosts\nColumns: host_address\nOutputFormat: json\n"
		utc_time = datetime(1970, 1,1)
    		#Shifting the fetching time to -15mins, for the time being
    		end_time = datetime.now() - timedelta(minutes=60)
		end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    		#start_time = end_time - timedelta(minutes=5)
		file_path = os.path.dirname(os.path.abspath(__file__))
        	path = [path for path in file_path.split('/')]

       		if len(path) <= 4 or 'sites' not in path:
            		raise Exception, "Place the file in appropriate omd site"
        	else:
            		site = path[path.index('sites') + 1]


                output = json.loads(rrd_main.get_from_socket(site,query))
		           
                for host_ip in output:
			modified_query = "select * from snmptt where agentip='%s' and traptime >='%s';" % (host_ip[0],end_time)
			trap_result = mysql_functions.mysql_execute(modified_query,"snmptt")
			mongo_db_store(site,trap_result)
        except SyntaxError, e:
            raise MKGeneralException(_("Can not get snmp alarm outputs: %s") % (e))
        except socket.error, msg:
            raise MKGeneralException(_("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))

def mongo_db_store(site,trap_result):
	trap_event_dict = {}
	db = mongo_functions.mongo_db_conn(site,"nocout_event_log")
	for row in trap_result:
		trap_event_dict = dict(traptime=row[11],event_name=row[1],
                                                        trapoid=row[3],discription=row[12],
                                                        agent_ip=row[7],severity=row[9],community=row[5],
							enterprise=row[4],uptime =row[10])
		print trap_event_dict 
		mongo_functions.mongo_db_insert(db,trap_event_dict,"snmp_alarm_event")
			

if __name__ == '__main__':
    snmp_alarm_extraction()


