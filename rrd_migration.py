import os
import time
import demjson
from datetime import datetime, timedelta
import copy
from xml.etree import ElementTree as ET
import subprocess
import pymongo
import rrd_main

def build_export(site,host,service):
    _folder = '/opt/omd/sites/%s/var/pnp4nagios/perfdata/%s/' % (site,host)
    tmp_service =service
    service = service.replace(' ','_')
    params = []
    m = 0
    file_paths = []
    temp_dict = {}
    data_dict = {
        "host": host,
        "service": service,
        "ds": {}
    }
    perf_data_list = []
    threshold_values = {}
    try:
        if service == 'PING':
        	tree = ET.parse(_folder + '_HOST_.xml')
        	myfile = '_HOST_'
        else:
            for file in os.listdir(_folder):
                if file.find(service):
                    myfile = service  
                tree = ET.parse(_folder + service +'.xml')
    except IOError, e:
	print e
	return 0
  

    root = tree.getroot()
    query = "GET services\nColumns: perf_data\nFilter: host_name = " +\
        "%s\nFilter: service_description = %s\nAnd: 2\n" %(host,tmp_service)
    query_output = rrd_main.get_from_socket(site, query)
    print '-- check output --'
    print query_output

    if query_output:
        threshold_values = get_threshold(query_output)

    for ds in root.findall('DATASOURCE'):
        params.append(ds.find('NAME').text)

	for param in params:
   		rrd_file = myfile +'_'+ '%s.rrd' % param
    	file_path = _folder + rrd_file
    	file_paths.append(file_path)
    

    for path in file_paths:
        m = -1
        
        data_series = do_export(site, path,params[file_paths.index(path)])
        print "-- data_series --"
        print data_series
        data_dict.update({
            "check_time": data_series.get('check_time'),
            "local_timestamp": data_series.get('local_timestamp'),
            "site": data_series.get('site')
        })
        data_dict.get('ds')[params[file_paths.index(path)]] = [{"meta": [], "data": []}]
        for d in data_series.get('data'):
            m += 1
            if d[-1]:
                temp_dict = dict(
                    time=data_series.get('check_time') + timedelta(minutes=m),
                    value=d[-1]
                )
                data_dict.get('ds').get(params[file_paths.index(path)])[0].get('data').append(temp_dict)
        data_dict.get('ds').get(params[file_paths.index(path)])[0].get('meta').append(threshold_values.get(params[file_paths.index(path)]))
    print "-- data_dict --"
    print data_dict

    status = insert_data(data_dict)
    print status
    print "\n"

def do_export(site, file_name,data_source):
    data_series = {}
    cmd_output ={}
    CF = 'AVERAGE'
    resolution = '-300sec';
    utc_time = datetime(1970, 1,1)
    #Shifting the fetching time to -15mins, for the time being
    end_time = datetime.now() - timedelta(minutes=15)
    start_time = end_time - timedelta(minutes=5)
    start_epoch = int((start_time - utc_time).total_seconds())
    end_epoch = int((end_time - utc_time).total_seconds())

    #Subtracting 5:30 Hrs to epoch times, to get IST
    start_epoch -= 19800
    end_epoch -= 19800

    cmd = '/omd/sites/%s/bin/rrdtool xport --json -s %s -e %s '\
        %(site, str(start_epoch), str(end_epoch))
    RRAs = ['MIN','MAX','AVERAGE']

    for RRA in RRAs:
    	cmd += 'DEF:%s_%s=%s:%d:%s XPORT:%s_%s:%s_%s '\
            %(data_source, RRA, file_name, 1, RRA, data_source,
                RRA, data_source, RRA)

    p=subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    cmd_output, err = p.communicate()

    try:
        cmd_output = demjson.decode(cmd_output)
    except demjson.JSONDecodeError, e:
        print e
        return data_series

    print "-- cmd_output --"
    print cmd_output
    legend = cmd_output.get('meta').get('legend')
    start_check = cmd_output['meta']['start']
    end_check = start_check+300
    start_check = datetime.fromtimestamp(start_check)
    end_check = datetime.fromtimestamp(end_check)
    local_timestamp = pivot_timestamp(start_check)
    data_series.update({
        "site": site,
        "legend": legend,
        "data" :cmd_output['data'],
        "start_time": start_check,
        "end_time": end_check,
        "check_time": start_check,
        "local_timestamp": local_timestamp
    })
    return data_series

def get_threshold(perf_data):
    threshold_values = {}

    if len(perf_data) == 1:
        return threshold_values

    for param in perf_data.split(" "):
        if ';' in param.split("=")[1]:
            threshold_values[param.split("=")[0]] = {
                "war": param.split("=")[1].split(";")[1],
                "cric": param.split("=")[1].split(";")[2],
                "cur": param.split("=")[1].split(";")[0]
            }
        else:
            threshold_values[param.split("=")[0]] = {
                "war": None,
                "cric": None,
                "cur": param.split("=")[1].strip("\n")
            }
    print "-- threshold_values --"
    print threshold_values
    return threshold_values

def pivot_timestamp(timestamp):
    t_stmp = timestamp + timedelta(minutes=-(timestamp.minute % 5))

    return t_stmp

def db_port(site_name=None):
    port = None
    if site_name:
        site = site_name
    else:
        file_path = os.path.dirname(os.path.abspath(__file__))
        path = [path for path in file_path.split('/')]

        if len(path) <= 4 or 'sites' not in path:
            raise Exception, "Place the file in appropriate omd site"
        else:
            site = path[path.index('sites') + 1]
    
    port_conf_file = '/opt/omd/sites/%s/etc/mongodb/mongod.d/port.conf' % site
    try:
        with open(port_conf_file, 'r') as portfile:
            port = portfile.readline().split('=')[1].strip()
    except IOError, e:
        print e

    return port

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

def insert_data(data_dict):
    port = None
    db  = None
    #Get the port for mongodb process, specific to this multisite instance
    port = db_port()

    #Get the mongodb connection object
    db = mongo_conn(
        host='localhost',
        port=int(port),
        db_name='nocout'
    )

    if db:
        print "-- db port --"
        print int(port)
        db.device_perf.insert(data_dict)
        return "Data Inserted into Mongodb"
    else:
        return "Data couldn't be inserted into Mongodb"

def rrd_migration_main(site,host,services):
	for service in services[0]:
		build_export(site,host,service)

"""if __name__ == '__main__':
    build_export('BT','AM-400','PING')
"""

