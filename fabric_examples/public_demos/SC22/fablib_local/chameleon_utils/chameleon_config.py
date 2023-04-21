#!/bin/python3
import os

#General imports
import os
import json

#os.environ["OS_PROJECT_ID"]=<os_project_id>
#os.environ["OS_PASSWORD"]=<os_password>
#os.environ["OS_USERNAME"]=<os_username>

#os.environ["OS_AUTH_URL"]='https://chi.uc.chameleoncloud.org:5000/v3'
#os.environ["OS_IDENTITY_API_VERSION"]='3'
#os.environ["OS_INTERFACE"]='public'
#os.environ["OS_PROTOCOL"]="openid"
#os.environ["OS_AUTH_TYPE"]="v3oidcpassword"
#os.environ["OS_IDENTITY_PROVIDER"]="chameleon"
#os.environ["OS_DISCOVERY_ENDPOINT"]="https://auth.chameleoncloud.org/auth/realms/chameleon/.well-known/openid-configuration"
#os.environ["OS_CLIENT_ID"]="keystone-uc-prod"
#os.environ["OS_ACCESS_TOKEN_TYPE"]="access_token"
#os.environ["OS_CLIENT_SECRET"]="none"
#os.environ["OS_REGION_NAME"]="CHI@UC"


def read_chameleon_rc(file_path):
    vars = {}

    # file_path = os.environ[‘HOME’]+”/work/fabric_config/fabric_rc”
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('export'):
                    var_name = line.split('=')[0].split('export')[1].strip()
                    var_value = line.split('=')[1].strip().strip('"').strip("'")
                    
                    vars[var_name] = var_value
                    
    return vars



def load_chameleon_rc_environment(chameleon_rc_file=None):
    chameleon_rc_dict = read_chameleon_rc(chameleon_rc_file)
                
    if "OS_PROJECT_ID" in chameleon_rc_dict:
        os.environ["OS_PROJECT_ID"]=chameleon_rc_dict["OS_PROJECT_ID"] 

    if "OS_USERNAME" in chameleon_rc_dict:
        os.environ["OS_USERNAME"]=chameleon_rc_dict["OS_USERNAME"] 
        
    if "OS_PASSWORD" in chameleon_rc_dict:
        os.environ["OS_PASSWORD"]=chameleon_rc_dict["OS_PASSWORD"] 

    if "OS_AUTH_URL" in chameleon_rc_dict:
        os.environ["OS_AUTH_URL"]=chameleon_rc_dict["OS_AUTH_URL"] 
        
    if "OS_IDENTITY_API_VERSION" in chameleon_rc_dict:
        os.environ["OS_IDENTITY_API_VERSION"]=chameleon_rc_dict["OS_IDENTITY_API_VERSION"] 
        
    if "OS_INTERFACE" in chameleon_rc_dict:
        os.environ["OS_INTERFACE"]=chameleon_rc_dict["OS_INTERFACE"] 
        
    if "OS_PROTOCOL" in chameleon_rc_dict:
        os.environ["OS_PROTOCOL"]=chameleon_rc_dict["OS_PROTOCOL"] 
        
    if "OS_AUTH_TYPE" in chameleon_rc_dict:
        os.environ["OS_AUTH_TYPE"]=chameleon_rc_dict["OS_AUTH_TYPE"] 
        
    if "OS_IDENTITY_PROVIDER" in chameleon_rc_dict:
        os.environ["OS_IDENTITY_PROVIDER"]=chameleon_rc_dict["OS_IDENTITY_PROVIDER"] 

    if "OS_DISCOVERY_ENDPOINT" in chameleon_rc_dict:
        os.environ["OS_DISCOVERY_ENDPOINT"]=chameleon_rc_dict["OS_DISCOVERY_ENDPOINT"] 
        
    if "OS_CLIENT_ID" in chameleon_rc_dict:
        os.environ["OS_CLIENT_ID"]=chameleon_rc_dict["OS_CLIENT_ID"] 
        
    if "OS_ACCESS_TOKEN_TYPE" in chameleon_rc_dict:
        os.environ["OS_ACCESS_TOKEN_TYPE"]=chameleon_rc_dict["OS_ACCESS_TOKEN_TYPE"] 

    if "OS_CLIENT_SECRET" in chameleon_rc_dict:
        os.environ["OS_CLIENT_SECRET"]=chameleon_rc_dict["OS_CLIENT_SECRET"] 
        
    if "OS_REGION_NAME" in chameleon_rc_dict:
        os.environ["OS_REGION_NAME"]=chameleon_rc_dict["OS_REGION_NAME"] 
    
    


