import pytest
from mock import Mock, patch
from nsg_checker.message_dispatcher import MessageDispatcher


def test_missing_o365():
    o365_rules = {
        "192.168.0.1/24", "192.168.1.1/24", "192.168.2.1/24", "192.168.3.1/24"
    }

    o365_azure_rules = {"192.168.0.1/24", "192.168.1.1/24", "192.168.2.1/24"}

    gsuite_rules = set()

    gsuite_azure_rules = set()

    dipatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                gsuite_azure_rules)

    assert dipatch.missing_o365 == {"192.168.3.1/24"}


def test_extra_gsuite():
    o365_rules = set()

    o365_azure_rules = set()

    gsuite_rules = {
        "200.168.0.1/24",
        "200.168.1.1/24",
        "200.168.2.1/24",
    }

    gsuite_azure_rules = {
        "200.168.0.1/24", "200.168.1.1/24", "200.168.2.1/24", "200.168.3.1/24"
    }

    dipatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                gsuite_azure_rules)

    assert dipatch.extra_gsuite == {"200.168.3.1/24"}


@patch('nsg_checker.message_dispatcher.logging.info')
def test_dispatch_runs(mock_log):
    o365_rules = set()

    o365_azure_rules = set()

    gsuite_rules = {
        "200.168.0.1/24",
        "200.168.1.1/24",
        "200.168.2.1/24",
    }

    gsuite_azure_rules = {
        "200.168.0.1/24", "200.168.1.1/24", "200.168.2.1/24", "200.168.3.1/24"
    }

    dispatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                 gsuite_azure_rules)

    dispatch.dispatch_message()

    mock_log.assert_called_with(
        "Finished running Azure NSG Watcher Function. Closing down...")
