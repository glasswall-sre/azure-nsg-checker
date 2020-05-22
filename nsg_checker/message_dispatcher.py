"""
MessageDispatcher for the Azure NSG Checker. It takes the IP sets, calculates
the differences between them and then dispatches the message.

Parameters:
    o365_rules (set): The set of current O365 SMTP IPv4 addresses.
    o365_azure_rules (set): The set of current O365 IPv4 addresses.
    gsuite_azure_rules (set): The set of current GSUITE SMTP IPv4 addresses on an Azure NSG.
    o365_rules (set): The set of current O365 IPv4 addresses address on an Azure NSG.

"""

import logging


class MessageDispatcher:
    def __init__(self, o365_rules, gsuite_rules, o365_azure_rules,
                 gsuite_azure_rules):

        self.missing_o365 = o365_rules.difference(o365_azure_rules)
        self.extra_o365 = o365_azure_rules - o365_rules
        self.missing_gsuite = gsuite_rules.difference(gsuite_azure_rules)
        self.extra_gsuite = gsuite_azure_rules - gsuite_rules

    def dispatch_message(self):
        """
        Dispatches the message to stdout. PLACEHOLDER for SNS work
        """

        logging.info(
            f"The following NSG rules are missing from O365: {self.missing_o365}"
        )

        logging.info(
            f"The following NSG rules are missing from GSUITE: {self.missing_gsuite}"
        )

        logging.info(
            f"These NSG rules for O365 are no longer needed: {self.extra_o365}"
        )

        logging.info(
            f"These NSG rules for GSuite are no longer needed: {self.extra_gsuite}"
        )

        logging.info(
            "Finished running Azure NSG Watcher Function. Closing down...")
