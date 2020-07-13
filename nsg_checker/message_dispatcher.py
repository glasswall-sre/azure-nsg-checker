"""
MessageDispatcher for the Azure NSG Checker. It takes the IP sets, calculates
the differences between them and then dispatches the message.

Parameters:
    o365_rules (set): The set of current O365 SMTP IPv4 addresses.
    o365_azure_rules (set): The set of current O365 IPv4 addresses.
    gsuite_azure_rules (set): The set of current GSUITE SMTP IPv4 addresses on an Azure NSG.
    o365_rules (set): The set of current O365 IPv4 addresses address on an Azure NSG.
    slack_oauth (str): The slack Oauth token.
    slack_channel (str): The slack channel to send notifications to.

"""

import logging
from slack import WebClient


class MessageDispatcher:
    def __init__(self, o365_rules, gsuite_rules, o365_azure_rules,
                 gsuite_azure_rules, slack_oauth, slack_channel):

        self.missing_o365 = o365_rules.difference(o365_azure_rules)
        self.extra_o365 = o365_azure_rules - o365_rules
        self.missing_gsuite = gsuite_rules.difference(gsuite_azure_rules)
        self.extra_gsuite = gsuite_azure_rules - gsuite_rules
        self.slack_client = WebClient(token=slack_oauth)
        self.slack_channel = slack_channel

    def dispatch_message(self):
        """
        Dispatches the message to stdout. PLACEHOLDER for SNS work
        """

        logging.info(
            f"Sending slack Azure NSG update to slack channel {self.slack_channel}"
        )

        slack_text = self.create_slack_message

        self.slack_client.chat_postMessage(channel=self.slack_channel,
                                           text=slack_text)

        logging.info(f"Sent slack message to {self.slack_channel}")

    def create_slack_message(self):
        """
        Creates the slack message to be sent to slack.

        Returns:
            The slack message in a format that can be read my users.
        """

        extra_o365_message, extra_gsuite_message = "", ""

        if self.missing_o365:
            missing_o365_message = f"The following NSG rules are missing from O365:\n\t{self.pretty_nsg_sets(self.missing_o365)}"
        else:
            missing_o365_message = "No O365 NSG rules are missing"

        if self.missing_gsuite:
            missing_gsuite_message = f"The following NSG rules are missing from GSUITE:\n\t{self.pretty_nsg_sets(self.missing_gsuite)}"
        else:
            missing_gsuite_message = "No GSUITE NSG rules are missing"

        if self.extra_o365:
            extra_o365_message = f"These NSG rules for O365 are no longer needed:\n\t {self.pretty_nsg_sets(self.extra_o365)}"

        if self.extra_gsuite:
            extra_gsuite_message = f"These NSG rules for GSUITE are no longer needed:\n\t {self.pretty_nsg_sets(self.extra_gsuite)}"

        result = '\n'.join(
            filter(None, [
                missing_o365_message, missing_gsuite_message,
                extra_o365_message, extra_gsuite_message
            ]))

        return result

    def pretty_nsg_sets(self, nsg_set):
        """
        Takes a set of nsg rules and pretty formats them into a bullet point list.

        Arguments:
            nsg_set (set(str)): Set of IPs with a subnet.

        Returns:
            A string with each nsg rule on a new line as a bullet point list.
        """
        print(nsg_set)
        pretty_list = '\n '.join(f"- {nsg}" for nsg in nsg_set)

        return pretty_list
