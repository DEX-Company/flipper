"""

Test helpers


"""

def process_payment_events(ocean, account):
    model = ocean.get_squid_model()
    ocn = model.get_squid_ocean(account)
    ocn.agreements.watch_provider_events(account._squid_account)
