import pymongo
import datetime

def main():
    conn = pymongo.Connection(host='localhost', port=27017)
    db = conn['nocout']
    doc = {'ds': {
        'rta': [{'value': 243.8138, 'time': datetime.datetime(2014, 6, 4, 11, 40)},
        {'value': 275.47131667, 'time': datetime.datetime(2014, 6, 4, 11, 41)},
        {'value': 330.2981, 'time': datetime.datetime(2014, 6, 4, 11, 42)},
        {'value': 289.12931667, 'time': datetime.datetime(2014, 6, 4, 11, 43)},
        {'value': 265.46866667, 'time': datetime.datetime(2014, 6, 4, 11, 44)},
        {'value': 277.04435, 'time': datetime.datetime(2014, 6, 4, 11, 45)}],
        'rtmin': [{'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 40)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 41)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 42)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 43)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 44)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 45)}],
        'rtmax': [{'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 40)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 41)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 42)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 43)}, {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 44)},
        {'value': None, 'time': datetime.datetime(2014, 6, 4, 11, 45)}],
        'pl': [{'value': 0.0, 'time': datetime.datetime(2014, 6, 4, 11, 40)}, {'value': 0.0, 'time': datetime.datetime(2014, 6, 4, 11, 41)},
        {'value': 0.0, 'time': datetime.datetime(2014, 6, 4, 11, 42)}, {'value': 0.0, 'time': datetime.datetime(2014, 6, 4, 11, 43)},
        {'value': 0.0, 'time': datetime.datetime(2014, 6, 4, 11, 44)}, {'value': 0.0, 'time': datetime.datetime(2014, 6, 4, 11, 45)}]
        },
        'service': 'PING', 'check_time': datetime.datetime(2014, 6, 4, 12, 31),
        'local_timestamp': datetime.datetime(2014, 6, 4, 12, 37), 'site': 'BT', 'host': 'AM-400'
        }

    db.device_perf.insert(doc)

if __name__ == '__main__':
    main()
