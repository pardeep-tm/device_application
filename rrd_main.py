import rrd_migration
import socket
import json
import os


class MKGeneralException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason


def get_host_services_name(site_name=None):
        try:
            query = "GET hosts\nColumns: host_name\nOutputFormat: json\n"
                
            output = json.loads(get_from_socket(site_name, query))
            print "-- socket query output --"
            print output
            print "\n"
            for host_name in output:
                modified_query = "GET hosts\nColumns: host_services\n" +\
                    "Filter: host_name = %s\nOutputFormat: json\n" % (host_name[0])
                output= json.loads(get_from_socket(site_name, modified_query))
                print "-- socket modified_query output --"
                print output[0]
                rrd_migration.rrd_migration_main(site_name, host_name[0], output[0])
            print "\n"
        except SyntaxError, e:
            raise MKGeneralException(("Can not get performance data: %s") % (e))
        except socket.error, msg:
            raise MKGeneralException(("Failed to create socket. Error code %s Error Message %s:") % (str(msg[0]), msg[1]))

def get_from_socket(site_name, query):
    socket_path = "/opt/omd/sites/%s/tmp/run/live" % site_name
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socket_path)
    s.send(query)
    s.shutdown(socket.SHUT_WR)
    output = s.recv(100000000)
    output.strip("\n")
    return output


    
if __name__ == '__main__':
    site = 'site1'
    get_host_services_name(site_name=site)
    