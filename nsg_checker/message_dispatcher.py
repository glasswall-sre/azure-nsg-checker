"""
MessageDispatcher to handle the creation and dispatching of a message to Slack.

Author:
    Alex Potter-Dixon <apotter-dixon@glasswallsolutions.com>
"""

import logging
from typing import Set

from slack import WebClient


class MessageDispatcher:
    def __init__(self, o365_rules: Set, gsuite_rules: Set,
                 o365_azure_rules: Set, gsuite_azure_rules: Set,
                 slack_oauth: str, slack_channel: str) -> None:
        """
        MessageDispatcher for the Azure NSG Checker. It takes the IP sets, calculates
        the differences between them and then dispatches the message.

        Attributes:
            missing_o365 (set): A set of missing O365 NSG rules.
            extra_o365 (set): A set of extra O365 NSG rules.
            missing_gsuite (set): A set of missing GSUITE NSG rules.
            extra_gsuite (set): A set of extra GSUITE NSG rules.
            slack_client (WebClient): Slack Client to dispatch messages.
            slack_channel (str): The slack channel ID to send notifications to.
        
        Args:
            o365_rules (set): The set of current O365 SMTP IPv4 addresses.
            o365_azure_rules (set): The set of current O365 IPv4 addresses.
            gsuite_azure_rules (set): The set of current GSUITE SMTP IPv4 addresses on an Azure NSG.
            o365_rules (set): The set of current O365 IPv4 addresses address on an Azure NSG.
            slack_oauth (str): The slack Oauth token.
            slack_channel (str): The slack channel ID to send notifications to.
        
        """

        self.missing_o365 = o365_rules.difference(o365_azure_rules)
        self.extra_o365 = o365_azure_rules - o365_rules
        self.missing_gsuite = gsuite_rules.difference(gsuite_azure_rules)
        self.extra_gsuite = gsuite_azure_rules - gsuite_rules
        self.slack_client = WebClient(token=slack_oauth)
        self.slack_channel = slack_channel

    def dispatch_slack_message(self):
        """
        Dispatches the message to stdout. PLACEHOLDER for SNS work
        """

        logging.info(
            f"Sending slack Azure NSG update to slack channel {self.slack_channel}"
        )

        slack_text = self.create_slack_message()

        self.slack_client.chat_postMessage(channel=self.slack_channel,
                                           text=slack_text)

        logging.info(f"Sent slack message to {self.slack_channel}")

    def create_slack_message(self) -> str:
        """
        Creates the slack message to be sent to slack.

        Returns:
            The slack message in a format that can be read my users.
        """
        intro_message = "Here is your update from the Azure NSG Watcher:\n"
        extra_o365_message, extra_gsuite_message = "", ""

        if self.missing_o365:
            missing_o365_message = f"The following SMTP Ingress NSG rules are missing for O365 Exchange:{self.pretty_nsg_sets(self.missing_o365)}"
        else:
            missing_o365_message = "No O365 NSG rules are missing"

        if self.missing_gsuite:
            missing_gsuite_message = f"The following SMTP Ingress NSG rules are missing for GSUITE Gmail:{self.pretty_nsg_sets(self.missing_gsuite)}"
        else:
            missing_gsuite_message = "No GSUITE NSG rules are missing"

        if self.extra_o365:
            extra_o365_message = f"These SMTP NSG rules for O365 Exchange are no longer needed:{self.pretty_nsg_sets(self.extra_o365)}"

        if self.extra_gsuite:
            extra_gsuite_message = f"These SMTP NSG rules for GSUITE Gmail are no longer needed:{self.pretty_nsg_sets(self.extra_gsuite)}"

        result = '\n'.join(
            filter(None, [
                intro_message, missing_o365_message, missing_gsuite_message,
                extra_o365_message, extra_gsuite_message
            ]))

        return result

    def pretty_nsg_sets(self, nsg_set: Set) -> str:
        """
        Takes a set of nsg rules and pretty formats them into a bullet point list.

        Arguments:
            nsg_set (set(str)): Set of IPs with a subnet.

        Returns:
            A string with each nsg rule on a new line as a bullet point list.
        """

        pretty_list = '\n '.join(f"\n\t- {nsg}" for nsg in nsg_set)

        return pretty_list
