# Stdlib imports
import datetime
import re
import logging

# Third party imports
from unittest.mock import patch, MagicMock
import src.db.gen_seed_data as gen

# Internal imports
import src.db.gen_seed_data as farmer
import src.db.data_lists as seeds



# accounts
def test_gen_dummydata_accounts():
    """
    email:         count
    first_name:    count
    last_name:     count
    role:          count + content (guest|host + N admins)
    created_at:    count + dtype + range
    """
    email_addresses, first_names, last_names, roles, timestamps = farmer.gen_dummydata_accounts()

    data = [email_addresses, first_names, last_names, roles, timestamps]

    # count check
    for item in data:
        assert len(item) == seeds.num_gen_dummydata

    # Check if first and last name matches email
    for email, first_name, last_name in zip(email_addresses, first_names, last_names):
        assert first_name in email
        assert last_name in email

    # sanity log
    for i in range(10):
        logging.info(email_addresses[i])
        logging.info(roles[i])
        logging.info(timestamps[i])
    logging.info("")

    # role check
    assert roles.count("admin") == seeds.admin_count

    # dtype + range
    for ts in timestamps:
        assert isinstance(ts, datetime.datetime)
        assert seeds.start_timestamp <= ts <= seeds.stop_timestamp



# credentials
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



# addresses
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



# accommodations
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



# images
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


# PAYMENT METHODS
@patch("src.db.gen_seed_data.db_connection")
@patch("src.db.gen_seed_data._fetch_table_ids")
def test_gen_dummydata_payment_methods(fetch_ids_mock, conn_mock):
    # Mock account ids
    fetch_ids_mock.return_value = [1, 2, 3]

    # Mock DB connection + cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    conn_mock.return_value = mock_conn

    # Run
    gen.gen_dummydata_payment_methods()

    # Assert DROP executed
    assert mock_cursor.execute.call_count >= 1

    # Assert executemany was called
    mock_cursor.executemany.assert_called_once()

    # Extract argument passed to executemany
    args, kwargs = mock_cursor.executemany.call_args
    _, rows_iterable = args
    rows = list(rows_iterable)

    # Basic shape checks
    assert all(len(row) == 3 for row in rows)     # (id, method, timestamp)
    assert all(row[1] in ["card", "paypal"] for row in rows)
    assert all(isinstance(row[2], datetime.datetime) for row in rows)

    # Commit + close called
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()



# CREDIT CARDS
@patch("src.db.gen_seed_data.db_connection")
@patch("src.db.gen_seed_data._fetch_table_ids_where")
def test_gen_dummydata_credit_cards(fetch_ids_mock, conn_mock):
    # Mock payment_methods ids
    fetch_ids_mock.return_value = [10, 20, 30]

    # Mock db
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    conn_mock.return_value = mock_conn

    gen.gen_dummydata_credit_cards()

    # executemany called
    mock_cursor.executemany.assert_called_once()
    args, kwargs = mock_cursor.executemany.call_args
    _, rows_iterable = args
    rows = list(rows_iterable)

    assert len(rows) == 3
    for row in rows:
        assert len(row) == 5            # (id, brand, last4, month, year)
        assert isinstance(row[2], int)  # last4
        assert 1 <= row[3] <= 12
        assert 2023 <= row[4] <= 2053

    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()



# PAYPAL
@patch("src.db.gen_seed_data.db_connection")
@patch("src.db.gen_seed_data._fetch_table_ids_where")
def test_gen_dummydata_paypal(fetch_ids_mock, conn_mock):
    # Mock IDs
    fetch_ids_mock.return_value = [101, 102]

    # Mock db
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    conn_mock.return_value = mock_conn

    gen.gen_dummydata_paypal()

    mock_cursor.executemany.assert_called_once()

    args, kwargs = mock_cursor.executemany.call_args
    _, rows_iterable = args
    rows = list(rows_iterable)

    assert len(rows) == 2

    for r in rows:
        payment_method_id, pp_user, email = r
        assert isinstance(payment_method_id, int)
        assert pp_user.startswith("PP-")
        assert "@" in email

    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


def test_gen_dummydata_payout_accounts():
    pass


def test_gen_dummydata_payouts():
    pass


def test_gen_dummydata_notifications():
    pass


