#!/usr/bin/env python3
import cloudgenix
import argparse
from cloudgenix import jd, jd_detailed, jdout
import yaml
import cloudgenix_settings
import sys
import logging
import os
import datetime
from datetime import datetime, timedelta
import sys
import json

# Global Vars
TIME_BETWEEN_API_UPDATES = 60       # seconds
REFRESH_LOGIN_TOKEN_INTERVAL = 7    # hours
SDK_VERSION = cloudgenix.version
SCRIPT_NAME = 'CloudGenix: Tunnel Reoptimization'
SCRIPT_VERSION = "1"

# Set NON-SYSLOG logging to use function name
logger = logging.getLogger(__name__)

####################################################################
# Read cloudgenix_settings file for auth token or username/password
####################################################################

sys.path.append(os.getcwd())
try:
    from cloudgenix_settings import CLOUDGENIX_AUTH_TOKEN

except ImportError:
    # Get AUTH_TOKEN/X_AUTH_TOKEN from env variable, if it exists. X_AUTH_TOKEN takes priority.
    if "X_AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('X_AUTH_TOKEN')
    elif "AUTH_TOKEN" in os.environ:
        CLOUDGENIX_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    else:
        # not set
        CLOUDGENIX_AUTH_TOKEN = None

def disable_reoptimization(cgx, site_name): 
    site_list = []
    site_n2id = {}
    for site in cgx.get.sites().cgx_content['items']:
        if site["element_cluster_role"] == "SPOKE":
            site_n2id[site["id"]] = site["name"]
            if site_name == "All-Sites":
                site_list.append(site["id"])
            elif site_name == site["name"]:
                site_list.append(site["id"])
    
    if site_list:
        for site in site_list:
            resp_text = cgx.get.site_extensions(site_id = site).text
            resp_data = json.loads(resp_text)
            found = False
            for item in resp_data["items"]:
                if item["name"] == "TunnelManager":
                    if item["conf"]["disable_reopt"]:
                        found = True
            if found:
                print("INFO: Tunnel reoptimization already disabled on {}".format(site_n2id[site]))
            else:
                data = {"name": "TunnelManager", "namespace": "tunnelmgr/tunnelreopt", "entity_id": "4501", "disabled": False, "conf": {"disable_reopt": True}}
                resp = cgx.post.site_extensions(site_id = site, data=data)
                if resp.cgx_status:
                    print("INFO: Tunnel reoptimization is disabled on {}".format(site_n2id[site]))
                else:
                    print("Error: Could not set tunnel reoptimization to disabled on {}".format(site_n2id[site]))
                    cloudgenix.jd_detailed(resp)
    else:
        print("No sites found by the name " + site_name)
    
    return

def enable_reoptimization(cgx, site_name): 
    site_list = []
    site_n2id = {}
    for site in cgx.get.sites().cgx_content['items']:
        if site["element_cluster_role"] == "SPOKE":
            site_n2id[site["id"]] = site["name"]
            if site_name == "All-Sites":
                site_list.append(site["id"])
            elif site_name == site["name"]:
                site_list.append(site["id"])
    
    if site_list:
        for site in site_list:
            resp_text = cgx.get.site_extensions(site_id = site).text
            resp_data = json.loads(resp_text)
            found = False
            for item in resp_data["items"]:
                if item["name"] == "TunnelManager":
                    if item["conf"]["disable_reopt"]:
                        found = True
                        resp = cgx.delete.site_extensions(extension_id=item["id"],site_id = site)
                        if resp.cgx_status:
                            print("INFO: Tunnel reoptimization is enabled on {}".format(site_n2id[site]))
                        else:
                            print("Error: Could not set tunnel reoptimization to enabled on {}".format(site_n2id[site]))
                            cloudgenix.jd_detailed(resp)
            if not found:
                print("INFO: Tunnel reoptimization is already enabled on {}".format(site_n2id[site]))
                
        
                    
    else:
        print("No sites found by the name " + site_name)
    
    return
                                 
def go():
    ############################################################################
    # Begin Script, parse arguments.
    ############################################################################

    # Parse arguments
    parser = argparse.ArgumentParser(description="{0}.".format(SCRIPT_NAME))

    # Allow Controller modification and debug level sets.
    config_group = parser.add_argument_group('Name', 'These options change how the configuration is loaded.')
    config_group.add_argument("--site", "-S", help="Site Name", required=True, default=None)
    config_group.add_argument("--reoptimization", "-R", help="Enable Tunnel Reoptimization", action='store_true')
    controller_group = parser.add_argument_group('API', 'These options change how this program connects to the API.')
    controller_group.add_argument("--controller", "-C",
                                  help="Controller URI, ex. "
                                       "Alpha: https://api-alpha.elcapitan.cloudgenix.com"
                                       "C-Prod: https://api.elcapitan.cloudgenix.com",
                                  default=None)
    controller_group.add_argument("--insecure", "-I", help="Disable SSL certificate and hostname verification",
                                  dest='verify', action='store_false', default=True)
    login_group = parser.add_argument_group('Login', 'These options allow skipping of interactive login')
    login_group.add_argument("--email", "-E", help="Use this email as User Name instead of prompting",
                             default=None)
    login_group.add_argument("--pass", "-PW", help="Use this Password instead of prompting",
                             default=None)
    debug_group = parser.add_argument_group('Debug', 'These options enable debugging output')
    debug_group.add_argument("--debug", "-D", help="Verbose Debug info, levels 0-2", type=int,
                             default=0)
                             
    args = vars(parser.parse_args())
    
    ############################################################################
    # Instantiate API
    ############################################################################
    cgx_session = cloudgenix.API(controller=args["controller"], ssl_verify=args["verify"])

    # set debug
    cgx_session.set_debug(args["debug"])

    ##
    # ##########################################################################
    # Draw Interactive login banner, run interactive login including args above.
    ############################################################################
    print("{0} v{1} ({2})\n".format(SCRIPT_NAME, SCRIPT_VERSION, cgx_session.controller))

    # login logic. Use cmdline if set, use AUTH_TOKEN next, finally user/pass from config file, then prompt.
    # check for token
    if CLOUDGENIX_AUTH_TOKEN and not args["email"] and not args["pass"]:
        cgx_session.interactive.use_token(CLOUDGENIX_AUTH_TOKEN)
        if cgx_session.tenant_id is None:
            print("AUTH_TOKEN login failure, please check token.")
            sys.exit()

    else:
        while cgx_session.tenant_id is None:
            cgx_session.interactive.login(user_email, user_password)
            # clear after one failed login, force relogin.
            if not cgx_session.tenant_id:
                user_email = None
                user_password = None

    ############################################################################
    # End Login handling, begin script..
    ############################################################################

    # get time now.
    curtime_str = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')

    # create file-system friendly tenant str.
    tenant_str = "".join(x for x in cgx_session.tenant_name if x.isalnum()).lower()
    cgx = cgx_session
    
    
    site_name = args["site"]
    reoptimization = args["reoptimization"]
    if reoptimization:
        enable_reoptimization(cgx, site_name) 
    else:
        disable_reoptimization(cgx, site_name)  
    # end of script, run logout to clear session.
    cgx_session.get.logout()

if __name__ == "__main__":
    go()