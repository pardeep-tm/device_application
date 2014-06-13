from mod_python import apache
import requests



def my_handler(req):
    #req.send_http_header()
    req.content_type = "text/html"
    req.write("hello")

    return apache.OK

def activate_host():
    activate_host_url = "http://omdadmin:omd@192.168.0.14/BT/check_mk/"+\
        "activate_changes.py?folder=nitin&mode=changelog&_action="+\
        "activate&_transid=-1"

    r = requests.get(activate_host_url)
    print "activate_host status :: "
    print r.status_code
    if r.status_code == 200:
        return True
    else:
        return False

def add_host_to_distributed(instance):
    payload ={}
    try:
        payload = {
            "host": instance.device_name,
            "attr_alias": instance.device_alias,
            "attr_ipaddress": instance.ip_address,
            "site": instance.sitename,
            "mode": "newhost",
            "folder": "",
            "_change_ipaddress": "on",
            "attr_tag_agent": "ping", #To be edited
            "attr_tag_networking": "lan", #To be edited
            "attr_tag_criticality": "prod",
            "_transid": "-1",
            "_change_site": "on",
            "_change_tag_agent": "on",
            "_change_contactgroups": "on",
            "_change_tag_networking": "on",
            "_change_alias": "on",
            "save": "Save & Finish"
        }
    except AttributeError, e:
        return 
    url = "http://omdadmin:omd@pardeep/BT/check_mk/wato.py"

    r = requests.get(url, params=payload)
    print "Url"
    print r.url
    print r.status_code

    return r.status_code
