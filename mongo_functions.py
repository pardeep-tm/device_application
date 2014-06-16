import pymongo
import rrd_migration
def mongo_conn(**kwargs):
	"""
    	Mongodb connection object
    	"""
    	DB = None
    	try:
        	CONN = pymongo.Connection(
            	host=kwargs.get('host'),
            	port=kwargs.get('port')
        	)
        	DB = CONN[kwargs.get('db_name')]
    	except pymongo.errors.PyMongoError, e:
       		raise pymongo.errors.PyMongoError, e
	return DB


def mongo_db_conn(site_name,db_name):
	db =None
        port = rrd_migration.db_port(site_name)

        #Get the mongodb connection object
        db = mongo_conn(
                host='localhost',
                port=int(port),
                db_name=db_name
         )
        return db

def mongo_db_insert(db,event_dict,flag):
        success = 0
        failure = 1
        if db:
                if flag == "serv_event":
                        db.nocout_service_event_log.insert(event_dict)
                elif flag == "host_event":
                        db.nocout_host_event_log.insert(event_dict)
                elif flag == "snmp_alarm_event":
                        db.nocout_snmp_trap_log.insert(event_dict)
		elif flag == "notification_event":
			db.nocout_notification_log.insert(event_dict)
                return success
        else:
                print "Mongo_db insertion failed"
                return failure

