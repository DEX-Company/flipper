"""

Test helpers


"""

import time

def process_payment_events(squid_agent, account):
    model = squid_agent.squid_model
    ocn = model.get_squid_ocean(account)
    ocn.agreements.watch_provider_events(account._squid_account)
    # allow for the watcher to startup and wait for the events on the block chain
    time.sleep(20)
#    sleep_timeout_time = time.time() + 10
#    while sleep_timeout_time > time.time():
#        time.sleep(1)
