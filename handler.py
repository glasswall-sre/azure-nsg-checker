
import base64
import json
import os
import uuid
import logging
from typing import Dict

import boto3
import srelogging
from nsg_checker.message_dispatcher import MessageDispatcher
from botocore.exceptions import ClientError
from nsg_checker.azure_nsg_checker import AzureNSGChecker


def run(event, context):   

    srelogging.configure_logging()
    logging.info("Running Azure NSG Watcher Function.")

    logging.debug("Retrieving environment variables.")
    o365_url = os.environ["O365_URL"] + str(uuid.uuid4())
    gsuite_netblocks = os.environ["GSUITE_NETBLOCKS"].split(",")  
    azure_credentials = get_secret(os.environ["AZURE_APP_SECRET_NAME"], os.environ["AWS_SECRET_REGION"])
    logging.debug("Successfully loaded all required environment variables.")


    nsg_checker = AzureNSGChecker(azure_credentials,                                 
                                  gsuite_netblocks, o365_url)

    o365_azure_result, gsuite_azure_result = nsg_checker.get_azure_nsg_rules(os.environ["AZURE_NSG_RGP"], os.environ["AZURE_NSG_NAME"])

    o365_rules = nsg_checker.get_o365_smtp_ipv4_cidrs()
    gsuite_rules = nsg_checker.get_gsuite_smtp_ipv4_cidrs()
    
    dispatcher = MessageDispatcher(o365_rules,gsuite_rules,o365_azure_result, gsuite_azure_result)

    dispatcher.dispatch_message()



def get_secret(secret_name: str, region_name: str)-> Dict:
    """
    Retrieves a secret from AWS secret manager. 

    Attributes:
        secret_name (str): Name of the secret.
        region_name (str): Region where the secret is stored.
    
    Raises:
        ClientError if there is an issue retrieving the secret requested.
    
    Returns:
        A Python Object being the secret requested.
    """

    logging.info(f"Retriving secret {secret_name}")
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            logging.critical(f"Unable to decrypt secret {secret_name}.")
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            logging.critical(f"Internal service error retrieving {secret_name}.")
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logging.critical(f"Invalid secret: {secret_name}.")
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logging.critical(f"Invalid request for secret: {secret_name}.")
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.critical(f"Unable to find secret: {secret_name}.")
            raise e
    else:
       
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    logging.info(f"Successfully retrieving secret {secret_name}")
    return json.loads(secret)
