import pytest
from munch import munchify

import nsg_checker
from nsg_checker.azure_nsg_checker import AzureNSGChecker


class MockServicePrincipalCredentials:
    def __init__(self, *args, **kwargs):
        pass


class MockNetworkManagementClient:
    def __init__(self, *args, **kwargs):
        pass

    class network_security_groups:
        def __init__(self, *args, **kwargs):
            pass

        def get(*args, **kwargs):

            result_1 = {
                "security_rules": [{
                    "destination_port_ranges": ["25"],
                    "name":
                    "gsuite_Rule_1",
                    "source_address_prefixes": ["192.168.0.1/24"]
                }, {
                    "destination_port_ranges": ["25"],
                    "name":
                    "gsuite-smtp-192.168.1.1-24-uksprod15c439088",
                    "source_address_prefixes": ["192.168.1.1/24"]
                }, {
                    "destination_port_ranges": ["25"],
                    "name":
                    "o365-smtp-192.168.2.1-24-uksprod1b75e0ca7",
                    "source_address_prefixes": ["192.168.2.1/24"]
                }, {
                    "destination_port_ranges": ["25"],
                    "name":
                    "o365_Rule_2",
                    "source_address_prefixes": ["192.168.3.1/24"]
                }, {
                    "destination_port_ranges": ["25"],
                    "name":
                    "Mimecast",
                    "source_address_prefixes": ["172.168.0.1/24"]
                }, {
                    "destination_port_ranges": ["443"],
                    "name":
                    "O365_443_Rule_3",
                    "source_address_prefixes": ["172.168.1.1/24"]
                }]
            }

            return munchify(result_1)


def create_mock_azure_network(monkeypatch):

    monkeypatch.setattr(nsg_checker.azure_nsg_checker,
                        "NetworkManagementClient", MockNetworkManagementClient)
    monkeypatch.setattr(nsg_checker.azure_nsg_checker,
                        "ServicePrincipalCredentials",
                        MockServicePrincipalCredentials)

    azure_credentials = {
        "client_id": "22222",
        "tenant_id": "22222",
        "key": "22222",
        "subscription_id": "2222"
    }

    return AzureNSGChecker(azure_credentials, "gsuite_blocks",
                           "https://www.google.com")


@pytest.fixture
def mock_azure_network(monkeypatch):

    return create_mock_azure_network(monkeypatch)
