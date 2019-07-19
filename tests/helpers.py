"""

Test helpers


"""

import time

def process_payment_events(squid_agent, account):
    model = squid_agent.squid_model
    ocn = model.get_squid_ocean(account)
    ocn.agreements.watch_provider_events(account._squid_account)
