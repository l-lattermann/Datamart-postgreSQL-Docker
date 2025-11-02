"""
test_gen_seed_data.py

Pytest suite to verify that all dynamic seed generators in src.db.gen_seed_data
produce the correct number of items, valid value ranges, and expected formats.

Covers:
- accounts
- credentials
- addresses
- accommodations
- images
Stubs for: calendar, payments, bookings, reviews, conversations, messages, payouts.
"""

# ---------------------------------------------------------------------------
# Stdlib imports
# ---------------------------------------------------------------------------
import datetime
import re
import logging

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------
import src.db.gen_seed_data as farmer
import src.db.data_lists as seeds


# ---------------------------------------------------------------------------
# accounts
# ---------------------------------------------------------------------------
def test_gen_dummydata_accounts():
    """
    email:         count
    first_name:    count
    last_name:     count
    role:          count + content (guest|host + N admins)
    created_at:    count + dtype + range
    """
    email_adresses, first_names, last_names, roles, timestamps = farmer.gen_dummydata_accounts()

    data = [email_adresses, first_names, last_names, roles, timestamps]

    # count check
    for item in data:
        assert len(item) == seeds.num_gen_dummydata

    # Check if first and last name matches email
    for email, first_name, last_name in zip(email_adresses, first_names, last_names):
        assert first_name in email
        assert last_name in email

    # sanity log
    for i in range(10):
        logging.info(email_adresses[i])
        logging.info(roles[i])
        logging.info(timestamps[i])
    logging.info("")

    # role check
    assert roles.count("admin") == seeds.admin_count

    # dtype + range
    for ts in timestamps:
        assert isinstance(ts, datetime.datetime)
        assert seeds.start_timestamp <= ts <= seeds.stop_timestamp


# ---------------------------------------------------------------------------
# credentials
# ---------------------------------------------------------------------------
def test_gen_dummydata_credentials():
    """
    password_hash:       count + length
    password_updated_at: count + dtype + range
    """
    password_hash, password_updated_at = farmer.gen_dummydata_credentials()
    data = [password_hash, password_updated_at]

    # count check
    for item in data:
        assert len(item) == seeds.num_gen_dummydata

    # sanity log
    for i in range(10):
        logging.info(password_hash[i])
        logging.info(password_updated_at[i])
    logging.info("")

    # password length
    for pwd in password_hash:
        assert len(pwd) == seeds.pwd_hash_length

    # dtype + range
    for ts in password_updated_at:
        assert isinstance(ts, datetime.datetime)
        assert seeds.start_timestamp <= ts <= seeds.stop_timestamp

    # keep inner stub as in original code (logic unchanged)
    def test_gen_dummydata_amenities():
        pass


# ---------------------------------------------------------------------------
# addresses
# ---------------------------------------------------------------------------
def test_gen_dummydata_addresses():
    """
    Verify generated address data.
    """
    line1, line2, city, postal_code, country = farmer.gen_dummydata_addresses()
    data = [line1, line2, city, postal_code, country]

    # count check
    for item in data:
        assert len(item) == seeds.num_gen_dummydata

    # sanity log
    for i in range(10):
        logging.info(line1[i])
        logging.info(line2[i])
        logging.info(city[i])
        logging.info(postal_code[i])
        logging.info(country[i])
    logging.info("")

    # value domain check
    for c in country:
        assert c in seeds.city_country.values()


# ---------------------------------------------------------------------------
# accommodations
# ---------------------------------------------------------------------------
def test_gen_dummydata_accommodations():
    """
    Verify generated accommodation data.
    """
    title, price_cents, is_active, created_at = farmer.gen_dummydata_accommodations()
    data = [title, price_cents, is_active, created_at]

    # count check
    for item in data:
        assert len(item) == seeds.num_gen_dummydata

    # sanity log
    for i in range(10):
        logging.info(title[i])
        logging.info(price_cents[i])
        logging.info(is_active[i])
        logging.info(created_at[i])
    logging.info("")


# ---------------------------------------------------------------------------
# images
# ---------------------------------------------------------------------------
def test_gen_dummydata_images():
    """
    Verify generated image data.
    """
    mime, storage_key, created_at = farmer.gen_dummydata_images()
    data = [mime, storage_key, created_at]

    # count check
    for item in data:
        assert len(item) == seeds.num_gen_dummydata*4

    # sanity log
    for i in range(10):
        logging.info(mime[i])
        logging.info(storage_key[i])
        logging.info(created_at[i])
    logging.info("")

    # dtype + range
    for ts in created_at:
        assert isinstance(ts, datetime.datetime)
        assert seeds.start_timestamp <= ts <= seeds.stop_timestamp

    # storage key format
    for key in storage_key:
        assert re.match(r"^images/[a-f0-9\-]{36}\.[a-z]{3,4}$", key)


# ---------------------------------------------------------------------------
# stubs for not-yet-implemented generators
# ---------------------------------------------------------------------------
def test_gen_dummydata_accommodation_calendar():
    pass


def test_gen_dummydata_payments():
    pass


def test_gen_dummydata_bookings():
    pass


def test_gen_dummydata_reviews():
    pass


def test_gen_dummydata_review_images():
    pass


def test_gen_dummydata_conversations():
    pass


def test_gen_dummydata_messages():
    pass


def test_gen_dummydata_payment_methods():
    pass


def test_gen_dummydata_credit_cards():
    pass


def test_gen_dummydata_paypal():
    pass


def test_gen_dummydata_payout_accounts():
    pass


def test_gen_dummydata_payouts():
    pass


def test_gen_dummydata_notifications():
    pass