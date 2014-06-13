from datetime import datetime, timedelta
import pymongo
import requests
import json
import ast
import time

from django.conf import settings


def dump_stats():
    """
    Get the data from check_mk livestatus and
    insert into mongodb 
    """

    db = mongo_conn('nocout')
    device = "nt"
    data_dict = {}
    chk_time = None
    t_stmp = None
    url = make_url(
        host_ip='192.168.0.14',
        name='GET services',
        filters_on={
            "host_name": "myhost8",
            "description": "PING"
        },
        attributes=[
            'perf_data',
            'next_check',
            'last_check',
            'service_last_check'
        ]
    )
    response = requests.get(url).text
    response = ast.literal_eval(eval(response))
    perf_data = response[0][0]
    next_check = response[0][1]
    last_check = response[0][2]
    chk_time = datetime.now()
    t_stmp = chk_time + timedelta(minutes=-(chk_time.minute % 5))
    t_stmp = datetime(
        t_stmp.year,
        t_stmp.month,
        t_stmp.day,
        t_stmp.hour,
        t_stmp.minute
    )
    data_dict.update({
        "device_name": device,
        "service_name": "ping",
        "last_check": last_check,
        "next_check": next_check,
        "perf_data": perf_data,
        "check_time": chk_time,
        "system_timestamp": t_stmp,
    })
    print data_dict
    #db.device_stats.insert(data_dict)

def make_url(**kwargs):
    """
    Make a call to livestatus API
    """
    filters = {}
    host_ip = kwargs.get('host_ip')
    name = kwargs.get('name')
    filters_on = kwargs.get('filters_on')
    attributes = kwargs.get('attributes')

    url = 'http://omdadmin:omd@%s/nms1/check_mk/collect_perf_data.py?' % host_ip

    filters.update({
        "name": name,
        "filters_on": filters_on,
        "attributes": attributes
    })
    url = url + 'new_query=%s' % filters

    return url

def mongo_conn(db_name):
    """
    Mongodb connection object
    """
    DB = None
    try:
        CLIENT = pymongo.MongoClient()
        DB = CLIENT[db_name]
    except pymongo.errors.PyMongoError, e:
        raise pymongo.errors.PyMongoError(e.message)
    return DB

if __name__ == "__main__":
    dump_stats()

