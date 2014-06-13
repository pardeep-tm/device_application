import os
import MySQLdb
import pymongo
from datetime import datetime, timedelta
from rrd_migration import mongo_conn, db_port
import subprocess


def main():
    data_values = []
    values_list = []
    docs = []
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)
    site_dirs = os.listdir('/opt/omd/sites/')

    docs = read_data('BT', start_time, end_time)
    print "-- docs --"
    print docs
    for doc in docs:
        values_list = build_data(doc)
    data_values.extend(values_list)
    print "-- data_values --"
    print data_values
    field_names = [
        'machine_id',
        'hostname',
        'service',
        'site_id',
        'ds',
        'cur_val',
        'min_val',
        'max_value',
        'avg_val',
        'system_timestamp',
        'check_timestamp'
    ]
    insert_data(field_names, data_values)

def read_data(site_name, start_time, end_time):
    db = None
    port = None
    docs = []
    start_time = datetime(2014, 6, 4, 12, 35)
    end_time = datetime(2014, 6, 4, 12, 40)
    #start_time = datetime(2014, 6, 5, 13, 20)
    #end_time = datetime(2014, 6, 5, 13, 30)
    print "-- start_time, end_time --"
    print start_time, end_time
    port = db_port(site_name=site_name)
    if port:
        db = mongo_conn(
            host='localhost',
            port=int(port),
            db_name='nocout'
        )
    if db:
        cur = db.device_perf.find({
            "local_timestamp": {"$gt": start_time, "$lt": end_time}
        })
        for doc in cur:
            docs.append(doc)
     
    return docs

def build_data(doc):
    values_list = []
    uuid = get_machineid()
    for ds in doc.get('ds').iterkeys():
        for entry in doc.get('ds').get(ds):
            epoch_time = get_epoch_time(entry.get('time'))
            t = (
                uuid,
                doc.get('host'),
                doc.get('service'),
                doc.get('site'),
                ds,
                entry.get('value'),
                entry.get('value'),
                entry.get('value'),
                entry.get('value'),
                doc.get('local_timestamp'),
                entry.get('time')
            )
            values_list.append(t)
            t = ()
    return values_list

def insert_data(field_names, data_values):
    pass

def get_epoch_time(datetime_obj):
    utc_time = datetime(1970, 1,1)
    epoch_time = datetime_obj
    if isinstance(datetime_obj, datetime):
        epoch_time = int((datetime_obj - utc_time).total_seconds())

    return epoch_time

def get_machineid():
    uuid = None
    proc = subprocess.Popen(
        'sudo -S dmidecode | grep -i uuid',
        stdout=subprocess.PIPE,
        shell=True
    )
    cmd_output, err = proc.communicate()
    if not err:
        uuid = cmd_output.split(':')[1].strip()
    else:
        uuid = err

    return uuid

if __name__ == '__main__':
    main()