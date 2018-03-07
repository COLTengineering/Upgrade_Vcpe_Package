"""
This Tool is designed for upgrading Versa CPE.
"""

__author__ = "Sathishkumar murugesan"
__copyright__ = "Copyright(c) 2018 Colt Technologies india pvt ltd."
__credits__ = ["Danny Pinto", "Anoop Jhon"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Sathishkumar Murugesan"
__email__ = "Sathishkumar.Murugesan@colt.net"
__status__ = "Developed"

import templates as t1
import json
import pandas as pd
from datetime import datetime
import logging
import logging.handlers
from Commands import *
import pprint
import getpass

LOGFILE = "LOGS/upgrade_log_" + str(datetime.now()) + ".log"
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=(1048576*5), backupCount=7)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



def main():
    logging.debug("SCRIPT STARTED")
    start_time = datetime.now()
    xl_file = 'upgrade_device_list.xlsx'
    pl = pd.read_excel(xl_file, 'Sheet1')
    vd_dict = get_vd_details()
    vdurl = 'https://' + vd_dict['ip'] + ':9182'
    user = vd_dict['user']
    passwd = vd_dict['passwd']
    upgrade_result = {}
    for i in range(len(pl.ix[:])):
        print "-" * 60
        print "|            DEVICE " + pl.ix[i, 'device_name_in_vd'] + "  Upgrade starts           |"
        print "-" * 60
        cpe_upgrade_result = 'FAILED'
        dev_dict = {}
        dev_dict["device_type"] = pl.ix[i, 'type']
        dev_dict["ip"] = pl.ix[i, 'ip']
        dev_dict["username"] = pl.ix[i, 'username']
        dev_dict["password"] = pl.ix[i, 'password']
        dev_dict["port"] = pl.ix[i, 'port']
        body_params = {
            'PACKAGE_NAME': pl.ix[i, 'package_name'],
            'DEVICE_NAME': pl.ix[i, 'device_name_in_vd']
        }
        body = config_template(t1.body_temp, body_params)
        json_data = json.loads(body)
        net_connect = make_connection(dev_dict)
        pack_info = get_package_info(net_connect)
        pprint.pprint(pack_info)
        print "**" * 40
        print "STEP 1 : CHECK PACKAGE INFO"
        print "**" * 40
        logging.debug("package info from CPE" + pack_info['PACKAGE_NAME'])
        logging.debug("package info from excel sheet" + pl.ix[i, 'package_info'])
        if pack_info['PACKAGE_NAME'] == pl.ix[i, 'package_info']:
            print pl.ix[i, 'device_name_in_vd'] + "     UPGRADE RESULT : FAILED"
            print "REASON: device already running with same package"
            print ">>" * 20 + "FAILED" + "<<" * 20
            upgrade_result[pl.ix[i, 'device_name_in_vd']] = 'FAILED - same package already available'
            print "-" * 60
            print "|            DEVICE " + pl.ix[i, 'device_name_in_vd'] + "  Upgrade Ends               |"
            print "-" * 60
            continue
        else:
            print "**" * 40
            print pl.ix[i, 'device_name_in_vd'] + " Package will be upgraded to " + pack_info['PACKAGE_NAME']
            print "**" * 40
        package_before_upgrade = pack_info['PACKAGE_NAME']
        timestamp = str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")).replace(" ", "")
        snapshot_desc = "PRE-UPGRADE-" + timestamp
        snapshot_timestamp = take_snapshot(net_connect, snapshot_desc)
        print "**" * 40
        print "STEP 2 : SNAPSHOT CREATED :" +snapshot_timestamp
        print "**" * 40
        time.sleep(20)
        #####REST OPERATIONS - begin #################
        print "**" * 40
        print "STEP 3: DO UPGRADE via REST API"
        rest_result = rest_operation(vdurl, user, passwd, json_data)
        print "**" * 40
        #####REST OPERATIONS - end #################
        close_connection(net_connect)
        time.sleep(5)
        net_connect = make_connection(dev_dict)
        # print "**" * 40
        # print "STEP 4 : DO ROLLBACK using SNAPSHOT"
        # print "**" * 40
        # rollback_snapshot(net_connect, snapshot_timestamp)
        time.sleep(50)
        pack_info_after_upgrade = get_package_info(net_connect)
        pprint.pprint(pack_info_after_upgrade)
        package_after_upgrade = pack_info_after_upgrade['PACKAGE_NAME']

        if package_after_upgrade == pl.ix[i, 'package_info']:
            print "Upgrade Success"
            print package_after_upgrade
            print pl.ix[i, 'package_info']
            print ">>" * 20 + pl.ix[i, 'device_name_in_vd'] + "   UPGRADE  REST API TASK STATUS: " + rest_result + "<<" * 20
            upgrade_result[pl.ix[i, 'device_name_in_vd']] = 'Upgrade SUCCESS'
        else:
            print "Upgrade failed. please check device."
            print ">>" * 20 + pl.ix[i, 'device_name_in_vd'] + "UPGRADE REST STATUS: " + rest_result + "<<" * 20
            upgrade_result[pl.ix[i, 'device_name_in_vd']] = 'Upgrade FAILED. Please check log for more details'
        print "-" * 60
        print "|            DEVICE " + pl.ix[i, 'device_name_in_vd'] + "  Upgrade Ends               |"
        print "-" * 60
    print "+" * 104
    print "++++" * 10 + ' UPGRADE SUMMARY REPORT ' + "++++" * 10
    print "+" * 104
    logging.debug("+" * 104)
    logging.debug("++++" * 10 + ' UPGRADE SUMMARY REPORT ' + "++++" * 10)
    logging.debug("+" * 104)
    for key, value in upgrade_result.iteritems():
        print key, ">--->", value
        logging.debug(key + ">--->" + value)
    print "+" * 104
    logging.debug("+" * 104)
    print "Time elapsed: {}\n".format(datetime.now() - start_time)


if __name__ == "__main__":
    main()