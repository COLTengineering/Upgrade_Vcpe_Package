import time
import requests
from string import Template
from netmiko import ConnectHandler
from Variables import *
import logging
import getpass


def get_vd_details():
    ip = raw_input("Enter Versa Director IP address:\n")
    print "Versa director IP:" + ip
    user = raw_input("Enter Versa Director Username:\n")
    print "Versa director IP:" + user
    passwd = raw_input("Enter Versa Director Password:\n")
    print "Versa director IP:" + passwd
    return {'ip' : ip, 'user': user, 'passwd' : passwd}


def config_template(text, params1):
    template = Template(text)
    txt = template.safe_substitute(params1)
    return txt


def make_connection(a_device):
    net_connect = ConnectHandler(**a_device)
    net_connect.enable()
    print net_connect
    time.sleep(5)
    print "{}: {}".format(net_connect.device_type, net_connect.find_prompt())
    print str(net_connect) + " connection opened"
    logging.debug(str(net_connect) + " connection opened")
    return net_connect


def close_connection(net_connect):
    net_connect.disconnect()
    print str(net_connect) + " connection closed"
    logging.debug(str(net_connect) + " connection closed")



def ping(net_connect, dest_ip, **kwargs):
    cmd = "ping " + str(dest_ip)
    paramlist = ['count', 'df_bit', 'interface', 'packet_size', 'rapid',
                 'record-route', 'routing_instance', 'source']
    for element in paramlist:
        if element in kwargs.keys():
            cmd =  cmd + " " + element.replace('_', '-') + " "+ str(kwargs[element])
    print cmd
    output = net_connect.send_command_expect(cmd)
    print output
    return str(" 0% packet loss" in output)


def get_snapshot(net_connect, desc):
    cmd = "show system snapshots | tab | match " + desc
    output = net_connect.send_command_expect(cmd)
    logging.debug(output)
    return output.split()[0]


def take_snapshot(net_connect, desc):
    cmd = "request system create-snapshot description " + str(desc) + " no-confirm"
    print cmd
    output = net_connect.send_command_expect(cmd)
    logging.debug(output)
    print output
    return get_snapshot(net_connect, desc)


def rollback_snapshot(net_connect, snapshot_timestamp):
    cmd = "request system rollback to " + snapshot_timestamp + " no-confirm"
    output = net_connect.send_command_expect(cmd)
    print output


def get_interface_status(net_connect, intf_name):
    """Get interface status. Return LAN VRF name and subnet"""
    cmd = 'show interfaces brief ' + str(intf_name) + ' | tab'
    print cmd
    output = net_connect.send_command_expect(cmd)
    logging.debug(output)
    output_string = str(output)
    print output_string
    output_list = output_string.split("\n")
    intf_dict = {}
    keys = output_list[0].split()
    values = output_list[2].split()
    for i in xrange(len(keys)):
        intf_dict[keys[i]] = values[i]
    return intf_dict


def get_package_info(net_connect):
    cmd = 'show system package-info | tab'
    output = net_connect.send_command_expect(cmd)
    logging.debug(output)
    output_string = str(output)
    print output_string
    output_list = output_string.split("\n")
    intf_dict = {}
    values = output_list[3].split()
    intf_dict['PACKAGE_ID'] = values[0]
    intf_dict['MAJOR'] = values[1]
    intf_dict['MINOR'] = values[2]
    intf_dict['DATE'] = values[3]
    intf_dict['PACKAGE_NAME'] = values[4]
    intf_dict['REL_TYPE'] = values[5]
    intf_dict['BUILD_TYPE'] = values[6]
    intf_dict['BRANCH'] = values[7]
    return intf_dict


def convert_string_dict(output_str):
    output_string = str(output_str)
    dict1 = {}
    for i in output_string.split("\n"):
        k = i.split()
        dict1[k[0]] = k[1:]
    return dict1


def rest_operation(vd, user, passwd, json_data):
    response = requests.post(vd + upgrade_dev_url,
                             auth=(user, passwd),
                             headers=headers2,
                             json=json_data,
                             verify=False)

    logging.debug(response.text)
    print response.text
    data = response.json()
    taskid = data['output']['result']['task']['task-id']
    print taskid
    logging.debug(taskid)
    percent_completed = 0
    while percent_completed < 100:
        response1 = requests.get(vd + task_url + taskid,
                                 auth=('MSK', 'Versa@123'),
                                 headers=headers2,
                                 verify=False)
        data1 = response1.json()
        logging.debug(data1)
        print data1
        percent_completed = data1['task']['percentage-completion']
        print percent_completed
        logging.debug(percent_completed)
        time.sleep(20)
    return  data1['task']['task-status']

