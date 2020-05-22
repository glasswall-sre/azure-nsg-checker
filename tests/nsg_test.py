import pytest
from mock import patch, Mock
from munch import munchify
import json
import requests
import dns.resolver

from urllib.request import Request, urlopen

from http.client import HTTPResponse
from dns.resolver import NXDOMAIN


def test_rebuild(mock_azure_network):

    assert mock_azure_network is not None


def test_just_get_o365_rules(mock_azure_network):

    o365_result, gsuite_result = mock_azure_network.get_azure_nsg_rules(
        "test", "test")

    assert o365_result == {'192.168.2.1/24', '192.168.3.1/24'}


def test_just_get_gsuite_rules(mock_azure_network):

    o365_result, gsuite_result = mock_azure_network.get_azure_nsg_rules(
        "test", "test")

    assert gsuite_result == {'192.168.1.1/24', '192.168.0.1/24'}


def test_just_get_25_rules(mock_azure_network):

    o365_result, gsuite_result = mock_azure_network.get_azure_nsg_rules(
        "test", "test")

    result = o365_result.union(gsuite_result)

    assert result == {
        '192.168.1.1/24', '192.168.0.1/24', '192.168.2.1/24', '192.168.3.1/24'
    }


@patch('nsg_checker.azure_nsg_checker.requests.get')
def test_o365_url_not_200(mock_requests, mock_azure_network):
    mock_http_response = Mock(spec=requests.Response)

    mock_http_response.status_code = 300

    mock_requests.return_value = mock_http_response

    result = mock_azure_network.get_o365_smtp_ipv4_cidrs()

    assert result == set()


@patch('nsg_checker.azure_nsg_checker.requests.get')
def test_o365_url_return_value(mock_requests, mock_azure_network):
    mock_http_response = Mock(spec=requests.Response)

    mock_http_response.status_code = 200
    mock_http_response.text = json.dumps([{
        "id":
        10,
        "serviceArea":
        "Exchange",
        "serviceAreaDisplayName":
        "Exchange Online",
        "urls": ["*.mail.protection.outlook.com"],
        "ips": [
            "40.92.0.0/15", "40.107.0.0/16", "52.100.0.0/14", "104.47.0.0/17",
            "2a01:111:f400::/48", "2a01:111:f403::/48"
        ],
        "tcpPorts":
        "25",
        "expressRoute":
        True,
        "category":
        "Allow"
    }])

    mock_requests.return_value = mock_http_response

    result = mock_azure_network.get_o365_smtp_ipv4_cidrs()

    assert result == {
        '40.92.0.0/15', '40.107.0.0/16', '104.47.0.0/17', '52.100.0.0/14'
    }


@patch('nsg_checker.azure_nsg_checker.dns.resolver.query')
def test_gsuite_return_value(mock_dns_resolver, mock_azure_network):
    mock_dns_response = Mock(spec=dns.resolver.Answer)

    mock_dns_response = [
        "v=spf1 ip4:35.190.247.0/24 ip4:64.233.160.0/19 ip4:66.102.0.0/20 ip4:66.249.80.0/20 ip4:72.14.192.0/18 ip4:74.125.0.0/16 ip4:108.177.8.0/21 ip4:173.194.0.0/16 ip4:209.85.128.0/17 ip4:216.58.192.0/19 ip4:216.239.32.0/19 ~all"
    ]

    mock_dns_resolver.return_value = mock_dns_response

    result = mock_azure_network.get_gsuite_smtp_ipv4_cidrs()

    assert result == {
        '35.190.247.0/24', '66.249.80.0/20', '66.102.0.0/20', '74.125.0.0/16',
        '209.85.128.0/17', '108.177.8.0/21', '173.194.0.0/16',
        '72.14.192.0/18', '64.233.160.0/19', '216.58.192.0/19',
        '216.239.32.0/19'
    }


@patch('nsg_checker.azure_nsg_checker.dns.resolver.query')
@patch('nsg_checker.azure_nsg_checker.logging.error')
def test_gsuite_error_handling(mock_dns_resolver, mock_log,
                               mock_azure_network):
    mock_dns_response = Mock(spec=dns.resolver.Answer)

    mock_dns_response = ["ip4:35.190.247.0/24"]

    mock_dns_resolver.return_value = mock_dns_response
    mock_dns_resolver.side_effect = NXDOMAIN()

    result = mock_azure_network.get_gsuite_smtp_ipv4_cidrs()

    assert result == set()
