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

    dispatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    assert dispatch.missing_o365 == {"192.168.3.1/24"}


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

    dispatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    assert dispatch.extra_gsuite == {"200.168.3.1/24"}


def test_message_extra_gsuite():
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
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    slack_text = dispatch.create_slack_message()

    assert slack_text == "Here is your update from the Azure NSG Watcher:\n\nNo O365 NSG rules are missing\nNo GSUITE NSG rules are missing\nThese SMTP NSG rules for GSUITE Gmail are no longer needed:\n\t- 200.168.3.1/24"


def test_message_extra_0365():
    o365_rules = {
        "201.168.0.1/24",
        "201.168.1.1/24",
        "201.168.2.1/24",
    }

    o365_azure_rules = {
        "201.168.0.1/24", "201.168.1.1/24", "201.168.2.1/24", "201.168.12.1/24"
    }

    gsuite_rules = {
        "200.168.0.1/24",
        "200.168.1.1/24",
        "200.168.2.1/24",
    }

    gsuite_azure_rules = {
        "200.168.0.1/24", "200.168.1.1/24", "200.168.2.1/24", "200.168.3.1/24"
    }

    dispatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    slack_text = dispatch.create_slack_message()

    assert slack_text == "Here is your update from the Azure NSG Watcher:\n\nNo O365 NSG rules are missing\nNo GSUITE NSG rules are missing\nThese SMTP NSG rules for O365 Exchange are no longer needed:\n\t- 201.168.12.1/24\nThese SMTP NSG rules for GSUITE Gmail are no longer needed:\n\t- 200.168.3.1/24"


def test_no_extra_message():
    o365_rules = {
        "201.168.0.1/24",
        "201.168.1.1/24",
        "201.168.2.1/24",
    }

    o365_azure_rules = {"201.168.0.1/24", "201.168.1.1/24", "201.168.2.1/24"}

    gsuite_rules = {
        "200.168.0.1/24",
        "200.168.1.1/24",
        "200.168.2.1/24",
    }

    gsuite_azure_rules = {"200.168.0.1/24", "200.168.1.1/24", "200.168.2.1/24"}

    dispatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    slack_text = dispatch.create_slack_message()

    assert slack_text == "Here is your update from the Azure NSG Watcher:\n\nNo O365 NSG rules are missing\nNo GSUITE NSG rules are missing"


def test_missing_o365_message():
    o365_rules = {
        "201.168.0.1/24", "201.168.1.1/24", "201.168.2.1/24", "202.168.3.1/24"
    }

    o365_azure_rules = {"201.168.0.1/24", "201.168.1.1/24", "201.168.2.1/24"}

    gsuite_rules = {
        "200.168.0.1/24",
        "200.168.1.1/24",
        "200.168.2.1/24",
    }

    gsuite_azure_rules = {"200.168.0.1/24", "200.168.1.1/24", "200.168.2.1/24"}

    dispatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    slack_text = dispatch.create_slack_message()

    assert slack_text == "Here is your update from the Azure NSG Watcher:\n\nThe following SMTP Ingress NSG rules are missing for O365 Exchange:\n\t- 202.168.3.1/24\nNo GSUITE NSG rules are missing"


def test_missing_gsuite_message():
    o365_rules = {
        "201.168.0.1/24",
        "201.168.1.1/24",
        "201.168.2.1/24",
    }

    o365_azure_rules = {"201.168.0.1/24", "201.168.1.1/24", "201.168.2.1/24"}

    gsuite_rules = {
        "200.168.0.1/24", "200.168.1.1/24", "200.168.2.1/24", "201.168.3.1/24"
    }

    gsuite_azure_rules = {"200.168.0.1/24", "200.168.1.1/24", "200.168.2.1/24"}

    dispatch = MessageDispatcher(o365_rules, gsuite_rules, o365_azure_rules,
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    slack_text = dispatch.create_slack_message()

    assert slack_text == "Here is your update from the Azure NSG Watcher:\n\nNo O365 NSG rules are missing\nThe following SMTP Ingress NSG rules are missing for GSUITE Gmail:\n\t- 201.168.3.1/24"


@patch('nsg_checker.message_dispatcher.logging.info')
@patch('nsg_checker.message_dispatcher.WebClient')
def test_dispatch_runs(mock_slack_client, mock_log):
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
                                 gsuite_azure_rules, "12343",
                                 "azure-nsg-checker")

    dispatch.dispatch_slack_message()

    mock_log.assert_called_with("Sent slack message to azure-nsg-checker")
