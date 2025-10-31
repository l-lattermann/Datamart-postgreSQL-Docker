# Test all the dynamic seed functions
import datetime
import re
import src.db.gen_seed_data as farmer
import src.db.data_lists as seeds
import logging



def test_gen_dummydata_accounts():
    """
    email: test if number of entities is correct,
    first_name:  test if number of entities is correct,
    last_name:  test if number of entities is correct, 
    role:  test if number of entities is correct, only users and hosts and 3 admins,
    created_at:  test if number of entities is correct, datatype is correct, range is correct
    """
    # Get the dummy data
    email_adresses, first_names, last_names, roles, timestamps = farmer.gen_dummydata_accounts()
    # Create iterable for easy handling
    data = [email_adresses, first_names, last_names, roles, timestamps]
    # Check count
    for item in data:
        assert seeds.num_gen_dummydata == len(item)
    
    # Sanity check
    for i in range(10):
        logging.info(data[0][i])
        logging.info(data[3][i])
        logging.info(data[4][i])
    logging.info('')
    # Check roles
    assert data[3].count('admin') == seeds.admin_count
    # Check timestamp dtype
    for item in data[4]:
        assert type(item) == datetime.datetime
    # Check timestamp range
    for date in data[4]:
        assert seeds.start_timestamp <= date <= seeds.stop_timestamp

def test_gen_dummydata_credentials():
    """
    password_hash: test if number of entities is correct,
    password_updated_at: test if number of entities is correct, datatype is correct, range is correct
    """
    # Get the dummy data
    password_hash, password_updated_at = farmer.gen_dummydata_credentials()
    # Create iterable for easy handling
    data = [password_hash, password_updated_at]
    # Check count
    for item in data:
        assert seeds.num_gen_dummydata == len(item)
    
    # Sanity check
    for i in range(10):
        logging.info(data[0][i])
        logging.info(data[1][i])
    logging.info('')

    # Check password hash length
    for pwd in data[0]:
        assert len(pwd) == seeds.pwd_hash_length

    # Check timestamp dtype
    for item in data[1]:
        assert type(item) == datetime.datetime
    # Check timestamp range
    for date in data[1]:
        assert seeds.start_timestamp <= date <= seeds.stop_timestamp

    def test_gen_dummydata_amenities():
        pass

def test_gen_dummydata_addresses():
    '''
    Test function checking the generated output from gen_dummydata_addresses.

    '''
    line1, line2, city, postal_code, country = farmer.gen_dummydata_addresses()
    # Create iterable for easy handling
    data = [line1, line2, city, postal_code, country]
    # Check count
    for item in data:
        assert seeds.num_gen_dummydata == len(item)

    # Sanity check
    for i in range(10):
        logging.info(data[0][i])
        logging.info(data[1][i])
        logging.info(data[2][i])
        logging.info(data[3][i])
        logging.info(data[4][i])
    logging.info('')

    # Check country names
    for country in data[4]:
        assert country in seeds.city_country.values()

def test_gen_dummydata_accommodations():
    '''
    Test function checking the generated output from gen_dummydata_accommodations.
    '''
    title, price_cents, is_active, created_at = farmer.gen_dummydata_accommodations()
    # Create iterable for easy handling
    data = [title, price_cents, is_active, created_at]
    # Check count
    for item in data:
        assert seeds.num_gen_dummydata == len(item)
    # Sanity check
    for i in range(10):
        logging.info(data[0][i])
        logging.info(data[1][i])
        logging.info(data[2][i])
        logging.info(data[3][i])
    logging.info('')

def test_gen_dummydata_images():
    '''
    Test function checking the generated output from gen_dummydata_images.
    '''
    # Get the dummy data
    mime, storage_key, created_at = farmer.gen_dummydata_images()
    # Create iterable for easy handling
    data = [mime, storage_key, created_at]
    # Check count
    for item in data:
        assert seeds.num_gen_dummydata == len(item) 
    # Sanity check
    for i in range(10):
        logging.info(data[0][i])
        logging.info(data[1][i])
        logging.info(data[2][i])
    logging.info('')
    # Check timestamp dtype
    for item in data[2]:
        assert type(item) == datetime.datetime
    # Check timestamp range
    for date in data[2]:
        assert seeds.start_timestamp <= date <= seeds.stop_timestamp
    # Check storage key format (simple regex for demo purposes)
    for key in data[1]:
        assert re.match(r"^images/[a-f0-9\-]{36}\.[a-z]{3,4}$", key)

def test_gen_dummydata_accommodation_calendar():
    '''
    Test function checking the generated output from gen_dummydata_accommodation_calendar.
    '''
    pass
def test_gen_dummydata_payments():
    '''
    Test function checking the generated output from gen_dummydata_payments.
    '''
    pass
def test_gen_dummydata_bookings():
    '''
    Test function checking the generated output from gen_dummydata_bookings.
    '''
    pass
def test_gen_dummydata_reviews():
    '''
    Test function checking the generated output from gen_dummydata_reviews.
    '''
    pass
def test_gen_dummydata_review_images():
    '''
    Test function checking the generated output from gen_dummydata_review_images.
    '''
    pass
def test_gen_dummydata_conversations():
    '''
    Test function checking the generated output from gen_dummydata_conversations.
    '''
    pass
def test_gen_dummydata_messages():
    '''
    Test function checking the generated output from gen_dummydata_messages.
    '''
    pass
def test_gen_dummydata_payment_methods():
    '''
    Test function checking the generated output from gen_dummydata_payment_methods.
    '''
    pass
def test_gen_dummydata_credit_cards():
    '''
    Test function checking the generated output from gen_dummydata_credit_cards.
    '''
    pass
def test_gen_dummydata_paypal():
    '''
    Test function checking the generated output from gen_dummydata_paypal.
    '''
    pass
def test_gen_dummydata_payout_accounts():
    '''
    Test function checking the generated output from gen_dummydata_payout_accounts.
    '''
    pass
def test_gen_dummydata_payouts():
    '''
    Test function checking the generated output from gen_dummydata_payouts.
    '''
    pass
def test_gen_dummydata_notifications():
    '''
    Test function checking the generated output from gen_dummydata_notifications.
    '''
    pass