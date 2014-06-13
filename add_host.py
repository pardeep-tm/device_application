from mod_python import apache
import requests
import wato
import json


def activate_host():
    activate_host_url = "http://omdadmin:omd@localhost/BT/check_mk/wato.py?folder=&mode=changelog&_action=activate&_transid=-1"

    r = requests.get(activate_host_url)
    #wato.ajax_activation()
    #if is_distributed() is True
    wato.ajax_replication()

    if r.status_code == 200:
        return True
    else:
        return False

def add_host():
    payload ={}
    host_tags = {
        "snmp": "snmp-only|snmp",
        "cmk_agent": "cmk-agent|tcp",
        "snmp_v1": "snmp-v1|snmp",
        "dual": "snmp-tcp|snmp|tcp",
        "ping": "ping"
    }

    try:
        payload = {
            "host": html.var("device_name"),
            "attr_alias": html.var("device_alias"),
            "attr_ipaddress": html.var("ip_address"),
            "site": html.var("site"),
            "mode": "newhost",
            "folder": "",
            "_change_ipaddress": "on",
            "attr_tag_agent": host_tags.get(html.var("agent_tag")),
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
        return "Unable To Add Host"
    url = "http://omdadmin:omd@localhost/BT/check_mk/wato.py"

    r = requests.get(url, params=payload)

    #return r.status_code

    html.write("Host Added To Multisite\n")
    html.write(json.dumps(payload))
    #Activate the changes
    activate_host()
    html.write("Host Activated For Monitoring\n")

def add_multisite_instance():
    payload = {}

    try:
        payload = {
            "id": html.var("name"),
            "alias": html.var("alias"),
            "_transid": "-1",
            "filled_in": "site",
            "folder": "",
            "method_1_0": html.var("site_ip"),
            "method_1_1": html.var("live_status_tcp_port"),
            "method_2": "",
            "method_sel": "1",
            "mode": "edit_site",
            "multisiteurl": "http://"  + html.var("site_ip") + "/" + html.var("name") + "/check_mk/",
            "repl_priority": "0",
            "replication": "slave",
            "save": "Save",
            "sh_host": "",
            "sh_site": "",
            "timeout": "10",
            "url_prefix": "http://" + html.var("site_ip") + "/" + html.var("name") + "/"
        }
    except AttributeError, e:
        return "Unable To Add Multisite"
    url = "http://omdadmin:omd@localhost/BT/check_mk/wato.py"  
    reply = requests.post(url,payload)
    html.write(json.dumps(payload))

    return reply.status_code

def login_page_multisite(site_id):
    try:
        payload = {
            "_login": site_id,
            "_transid": "-1",
            "folder": "",
            "mode": "sites"
        }
    except AttributeError, e:
        return "Unable To Login Multisite"

    url = "http://omdadmin:omd@localhost/BT/check_mk/wato.py"

    r = requests.get(url, params=payload)
    html.write("Logged-in to multisite\n")

    login_multisite(site_id)

def login_multisite(site_id):
    try:
        payload = {
            "_do_login": "Login",
            "_login": site_id,
            "_name": "omdadmin",
            "_passwd": "omd",
            "_transid": "-1",
            "filled_in": "login",
            "folder": "",
            "mode": "sites"
        }
    except AttributeError, e:
        return "Unable To Activate Multisite"

    url = "http://omdadmin:omd@localhost/BT/check_mk/wato.py"

    r = requests.get(url, params=payload)
    html.write("Multisite Activated\n")