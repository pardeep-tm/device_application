import os,json
from datetime import datetime, timedelta
import rrd_migration,rrd_main,mysql_functions,mongo_functions
				

def extract_nagios_events_live():
	db = None
	file_path = os.path.dirname(os.path.abspath(__file__))
        path = [path for path in file_path.split('/')]

        if 'sites' not in path:
                raise Exception, "File is not in omd specific directory"
        else:
                site = path[path.index('sites')+1]
	
	utc_time = datetime(1970, 1,1)
        start_time = datetime.now() - timedelta(minutes=10)
        end_time = datetime.now()
        start_epoch = int((start_time - utc_time).total_seconds())
        end_epoch = int((end_time - utc_time).total_seconds())

        # sustracting 5.30 hours        
        start_epoch -= 19800
        end_epoch -= 19800
        host_event_dict ={}
        serv_event_dict={}
        db = mongo_functions.mongo_db_conn(site,"nocout_event_log")
	query = "GET log\nColumns: log_type log_time log_state_type log_state  host_name service_description options host_address\nFilter: log_time >= %s\nFilter: class = 0\nFilter: class = 1\nFilter: class = 2\nFilter: class = 3\nFilter: class = 4\nFilter: class = 6\nOr: 6\n" %(start_epoch) 
	output= rrd_main.get_from_socket(site, query)
	#print output
	for log_attr in output.split('\n'):
		log_split = [log_split for log_split in log_attr.split(';')]
		print log_split
		if log_split[0] == "CURRENT HOST STATE":
			host_ip = log_split[11]
                        #host_ip = log_split[10].split(':')[0]
                        #host_ip = host_ip.split('-')[1]
                        host_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[7],
                                                        state_type=log_split[2],discription=log_split[11],
                                                        ip_address=host_ip,event_type_name=log_split[0])
		
               		mongo_functions.mongo_db_insert(db,host_event_dict,"host_event")
		elif log_split[0] == "CURRENT SERVICE STATE":
			host_ip = log_split[12]

                        #host_ip = log_split[11].split(':')[0]
                        #host_ip = host_ip.split('-')[1]
                        serv_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[8],
                                                        state_type=log_split[2],discription=log_split[11],
                                                        ip_address=host_ip,event_type_name=log_split[0],event_name=log_split[5])
                        #print serv_event_dict
                        mongo_functions.mongo_db_insert(db,serv_event_dict,"serv_event")
	

		elif log_split[0] == "HOST ALERT":
			
			host_ip = log_split[11]
			#host_ip = log_split[10].split(':')[0]
			#host_ip = host_ip.split('-')[1]
			host_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[7],
                                                        state_type=log_split[2],discription=log_split[10],
                                                        ip_address=host_ip,event_type_name=log_split[0])
                	#print host_event_dict
               		mongo_functions.mongo_db_insert(db,host_event_dict,"host_event")
		elif log_split[0] == "HOST FLAPPING ALERT":
			host_ip = log_split[11]
			host_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[7],
                                                        state_type=None,discription=log_split[8],
                                                        ip_address=host_ip,event_type_name=log_split[0])
			mongo_functions.mongo_db_insert(db,host_event_dict,"host_event")
		elif log_split[0] == "SERVICE ALERT":
			
			host_ip = log_split[11]

			#host_ip = log_split[11].split(':')[0]
			#host_ip = host_ip.split('-')[1]
			serv_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[8],
                                                        state_type=log_split[2],discription=log_split[11],
                                                        ip_address=host_ip,event_type_name=log_split[0],event_name=log_split[5])
			#print serv_event_dict
               		mongo_functions.mongo_db_insert(db,serv_event_dict,"serv_event")

		elif log_split[0] == "SERVICE FLAPPING ALERT":
			serv_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[8],
                                                        state_type=None,discription=log_split[9],
                                                        ip_address=None,event_type_name=log_split[0],event_name=log_split[5])
			mongo_functions.mongo_db_insert(db,serv_event_dict,"serv_event")

		elif log_split[0] == "HOST NOTIFICATION":
			host_ip = log_split[11]
                        #host_ip = log_split[10].split(':')[0]
                        #host_ip = host_ip.split('-')[1]
                        host_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[7],
                                                        state_type=log_split[2],discription=log_split[10],
                                                        ip_address=host_ip,event_type_name=log_split[0])
                        #print host_event_dict
                        mongo_functions.mongo_db_insert(db,host_event_dict,"notification_event")

		elif log_split[0] == "SERVICE NOTIFICATION":

                        host_ip = log_split[12]

                        #host_ip = log_split[11].split(':')[0]
                        #host_ip = host_ip.split('-')[1]
                        serv_event_dict=dict(time=log_split[1],host_name=log_split[4],status=log_split[9],
                                                        state_type=log_split[2],discription=log_split[11],
                                                        ip_address=host_ip,event_type_name=log_split[0],event_name=log_split[5])
                        #print serv_event_dict
                        mongo_functions.mongo_db_insert(db,serv_event_dict,"notification_event")
	
		
if __name__ == '__main__':
    extract_nagios_events_live()
