"""AzureNSGChecker

Main business logic to handle the retrieval of IPv4 addresses for O365 and GSuite.

Parameters:
    azure_credentials (Dict): Dictionary containing the Azure App's client_id, tenant_id and key.
    subscription (str): The subscription where the Azure NSG is located.
    gsuite_netblocks (List[str]): List of GSUITE netblocks.
    o365_url (str): The O365 URL for exchange endpoints.
    

Author:
    Alex Potter-Dixon <apotter-dixon@glasswallsolutions.com>
"""

import ipaddress
import json
import logging
import re
import uuid
from typing import List, Tuple, Dict, Set

import dns.resolver
import requests
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network import NetworkManagementClient

# IPv4 with CIDR Regex Pattern
IPV4_PATTERN = r"(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?"


class AzureNSGChecker:
    def __init__(self, azure_credentials: Dict, gsuite_netblocks: List[str],
                 o365_url: str):
        self.client = self._connect(azure_credentials["client_id"],
                                    azure_credentials["tenant_id"],
                                    azure_credentials["key"],
                                    azure_credentials["subscription_id"])

        self.gsuite_netblocks = gsuite_netblocks
        self.o365_url = o365_url

    def _connect(self, client_id: str, tenant_id: str, key: str,
                 subscription: str) -> NetworkManagementClient:
        """Connects to the NetworkManagementClient data client.

        Arguments:
            client_id (str): The Client ID of the Azure app.
            tenant_id (str): The Tenant ID of the Azure app.
            key (str): The client secret of the Azure app.

        Returns:
            NetworkManagementClient: The client of azure log analytics data endpoint.
        """
        logging.info("Connecting to Network Management Client.")
        credentials = ServicePrincipalCredentials(
            client_id=client_id,
            secret=key,
            tenant=tenant_id,
        )

        client = NetworkManagementClient(credentials,
                                         subscription,
                                         base_url=None)
        logging.info(
            "Successfully connected to the Network Management client.")

        return client

    def get_azure_nsg_rules(self, rgp_name: str,
                            nsg_name: str) -> Tuple[Set, Set]:
        """Retrieves the Azure NSG rules with GSUITE and O365 in their name
           and the SMTP Port 25.

        Arguments:
            rgp_name (str): The resource group name that contains the NSG.
            nsg_name (str): The name of the NSG inside the above rgp.

        Returns:
            Tuple (Set,Set): Two sets, first O365 rules found in the Azure NSG
            and a second set of GSUITE rules found in the Azure NSG.
        """
        logging.info(f"Retriving NSG rules for nsg {nsg_name} ")
        azure_result = self.client.network_security_groups.get(
            rgp_name, nsg_name)
        o365_result = set()
        gsuite_result = set()

        for rule in azure_result.security_rules:
            logging.info(rule.destination_port_range)
            if rule.destination_port_range == "25":
                logging.info(rule.name.lower())
                if "gsuite" in rule.name.lower():
                    gsuite_result.add(rule.source_address_prefix)
                elif "o365" in rule.name.lower():
                    o365_result.add(rule.source_address_prefix)

        logging.info(f"Successfully retrieving NSG rules for {nsg_name}")
        logging.info(f"O365 Rules found: {o365_result}")
        logging.info(f"GSUITE Rules found: {gsuite_result}")

        return (o365_result, gsuite_result)

    def get_o365_smtp_ipv4_cidrs(self) -> Set:
        """Retrieves the current Office 365 Exchange SMTP egress CIDR IPv4s
           addresses in a set.

           Contacts the outlook endpoint and retrieves all SMTP 25 IPv4 addresses.

           Returns:
                Set of O365 IPv4 CIDR.
        """
        logging.info(f"Retrieving exchange IPv4 CIDRS from {self.o365_url}")
        response = requests.get(self.o365_url)
        ipv4_addresses = set()

        if response.status_code != 200:
            logging.error(
                f"{response.status_code} returned by O365. No O365 rules retrieved."
            )
            return ipv4_addresses

        logging.info("Successfully retrieved O365 exchange IPv4 addresses.")

        response_data = json.loads(response.text)
        for service_area in response_data:
            for url in service_area["urls"]:
                if ".outlook.com" in url and "25" in service_area["tcpPorts"]:
                    for cidr in service_area["ips"]:
                        if isinstance(ipaddress.ip_network(cidr),
                                      ipaddress.IPv4Network):

                            ipv4_addresses.add(cidr)
        logging.debug(f"O365 IPv4 CIDR addresses found: {ipv4_addresses}.")
        return ipv4_addresses

    def get_gsuite_smtp_ipv4_cidrs(self) -> Set:
        """Retrieves the current GSUITE SMTP egress CIDR IPv4s 
           addresses in the format of a set.

           Returns:
              Set of GSUITE IPv4 egress CIDR IPs.

        """
        pat = re.compile(IPV4_PATTERN)
        ipv4_addresses = set()

        for netblock in self.gsuite_netblocks:
            try:
                logging.info(f"Performing DNS lookup for {netblock}")
                answers = dns.resolver.query(netblock, 'TXT')
                for rdata in answers:
                    ips = pat.findall(str(rdata))
                    ipv4_addresses.update(ips)
                logging.info(
                    f"Successfully performed DNS lookup for {netblock}")

            except dns.resolver.NXDOMAIN:
                logging.error(f"Unable to resolve: {netblock}")
            except dns.resolver.Timeout:
                logging.error(f"Timeout trying to resolve: {netblock}")
            except dns.resolver.NoNameservers:
                logging.warning(f"No nameserver to resolve: {netblock}")
            except dns.resolver.NoAnswer:
                logging.error(f"No dns answer: {netblock}")

        logging.debug(f"GSUITE IPv4 CIDR addresses found: {ipv4_addresses}.")

        return ipv4_addresses
