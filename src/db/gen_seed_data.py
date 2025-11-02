"""
dummy_data_generator.py

Generate generic, schema-aligned dummy data for seeding the database.

Provides generators for:
- accounts
- credentials
- addresses
- accommodations
- images
- (stubs) calendar, payments, bookings, reviews, conversations, messages, payouts

Assumptions:
- seed parameters and word lists live in src.db.data_lists as `seeds`
- timestamps are generated in a uniform window [start_timestamp, stop_timestamp]
- number of rows is controlled by seeds.num_gen_dummydata
"""

# ---------------------------------------------------------------------------
# Stdlib imports
# ---------------------------------------------------------------------------
import random
import datetime
from pathlib import Path
import sys

# ---------------------------------------------------------------------------
# Third-party / extra imports
# ---------------------------------------------------------------------------
import rstr

# ---------------------------------------------------------------------------
# Path/bootstrap
# Go two levels up if needed (src/db → project root). Keep logic unchanged.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Internal imports
# ---------------------------------------------------------------------------
import src.db.data_lists as seeds
from src.db.connection import db_connection  # kept although not used in current funcs


# ---------------------------------------------------------------------------
# ACCOUNTS
# ---------------------------------------------------------------------------
def gen_dummydata_accounts():
    """
    Fill dummy data for accounts table.

    Returns:
        email_adresses, first_names, last_names, roles, timestamps
    """
    # first names
    first_names = []
    for dummy_id in range(seeds.num_gen_dummydata):
        name = ""
        syllable_ammount = random.randint(seeds.fn_min_sylls, seeds.fn_max_sylls)
        for _ in range(syllable_ammount):
            name += random.choice(seeds.first_name_syllables)
        first_names.append(name)

    # last names
    last_names = []
    for dummy_id in range(seeds.num_gen_dummydata):
        name = ""
        syllable_ammount = random.randint(seeds.ln_min_sylls, seeds.ln_max_sylls)
        for _ in range(syllable_ammount):
            name += random.choice(seeds.last_name_syllables)
        last_names.append(name)

    # email addresses
    email_adresses = []
    for dummy_id in range(seeds.num_gen_dummydata):
        email_adress = (
            first_names[dummy_id]
            + "."
            + last_names[dummy_id]
            + "@"
            + random.choice(seeds.email_domains)
        )
        email_adresses.append(email_adress)

    # timestamps
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    timestamps = []
    for dummy_id in range(seeds.num_gen_dummydata):
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        timestamps.append(random_timestamp)

    # roles
    roles = []
    for dummy_id in range(seeds.num_gen_dummydata - seeds.admin_count):
        roles.append(random.choice(["guest", "host"]))
    for dummy_id in range(seeds.admin_count):
        roles.append("admin")

    return email_adresses, first_names, last_names, roles, timestamps


# ---------------------------------------------------------------------------
# CREDENTIALS
# ---------------------------------------------------------------------------
def gen_dummydata_credentials():
    """
    Fill dummy data for credentials table.

    Returns:
        password_hash, password_updated_at
    """
    password_hash = []
    for dummy_id in range(seeds.num_gen_dummydata):
        password = "".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()",
                k=seeds.pwd_hash_length,
            )
        )
        password_hash.append(password)

    # timestamps
    password_updated_at = []
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    timestamps = []
    for dummy_id in range(seeds.num_gen_dummydata):
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        timestamps.append(random_timestamp)
        password_updated_at.append(random_timestamp)

    return password_hash, password_updated_at


# ---------------------------------------------------------------------------
# ADDRESSES
# ---------------------------------------------------------------------------
def gen_dummydata_addresses():
    """
    Fill dummy data for addresses table.

    Returns:
        line1, line2, city, postal_code, country
    """
    line1 = []
    line2 = []
    cities = []
    postal_code = []
    countries = []

    for _ in range(seeds.num_gen_dummydata):
        city, postal = random.choice(list(seeds.city_postal.items()))
        country_name = seeds.city_country[city]
        street = random.choice(seeds.city_streets[city])
        house_number = str(random.randint(1, 200))

        # line1
        line1.append(f"{street} {house_number}")

        # optional line2
        if city in seeds.city_address_terms.keys():
            term1, term2 = seeds.city_address_terms[city]
            building_number = str(random.randint(1, 10))
            unit_number = str(random.randint(1, 50))
            line2.append(f"{term1} {building_number}, {term2} {unit_number}")

        cities.append(city)
        postal_code.append(postal)
        countries.append(country_name)

    return line1, line2, cities, postal_code, countries


# ---------------------------------------------------------------------------
# ACCOMMODATIONS
# ---------------------------------------------------------------------------
def gen_dummydata_accommodations():
    """
    Fill dummy data for accommodations table.

    Returns:
        titles, price_cents, is_active, created_at
    """
    titles = []
    price_cents = []
    is_active = []
    created_at = []

    # titles
    for _ in range(seeds.num_gen_dummydata):
        title = [
            random.choice(seeds.accomodation_title_words_dict["adjectives_general"]),
            random.choice(seeds.accomodation_title_words_dict["accommodation_nouns"]),
            random.choice(seeds.accomodation_title_words_dict["location_connectors"]),
            random.choice(seeds.accomodation_title_words_dict["adjectives_location"]),
            random.choice(seeds.accomodation_title_words_dict["place_names"]),
        ]
        titles.append(" ".join(title))
        print(title)

    # prices
    for _ in range(seeds.num_gen_dummydata):
        price = random.randint(50, 500) * 100
        price_cents.append(price)

    # activity flags
    for _ in range(seeds.num_gen_dummydata):
        is_active.append(random.choice([True, False]))

    # created_at
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    for _ in range(seeds.num_gen_dummydata):
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        created_at.append(random_timestamp)

    return titles, price_cents, is_active, created_at


# ---------------------------------------------------------------------------
# IMAGES
# ---------------------------------------------------------------------------
def gen_dummydata_images():
    """
    Fill dummy data for images table.

    Returns:
        mimes, storage_keys, created_at
    """
    mimes = []
    storage_keys = []
    created_at = []

    for _ in range(seeds.num_gen_dummydata):
        # mime
        mime = random.choice(seeds.image_mimes)
        mimes.append(mime)

        # timestamp
        time_delta = seeds.stop_timestamp - seeds.start_timestamp
        random_time_step = datetime.timedelta(
            seconds=random.randint(0, int(time_delta.total_seconds()))
        )
        random_timestamp = seeds.start_timestamp + random_time_step
        created_at.append(random_timestamp)

        # storage key
        storage_key = "images/"
        storage_key += rstr.xeger(
            r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
        )
        storage_key += f".{mime.split('/')[1]}"
        storage_keys.append(storage_key)

    return mimes, storage_keys, created_at


# ---------------------------------------------------------------------------
# STUBS FOR REMAINING TABLES
# Keep stubs to preserve structure. Implement later.
# ---------------------------------------------------------------------------
def gen_dummydata_accommodation_calendar():
    """
    Fill dummy data for accommodation_calendar table.

    Returns:
        day, is_blocked, price_cents, min_nights
    """
    days = []
    is_blocked = []
    price_cents = []
    min_nights = []

    return days, is_blocked, price_cents, min_nights


def gen_dummydata_payments():
    """
    Fill dummy data for payments table.
    """
    pass


def gen_dummydata_bookings():
    """
    Fill dummy data for bookings table.
    """
    pass


def gen_dummydata_reviews():
    """
    Fill dummy data for reviews table.
    """
    pass


def gen_dummydata_review_images():
    """
    Fill dummy data for review_images table.
    """
    pass


def gen_dummydata_conversations():
    """
    Fill dummy data for conversations table.
    """
    pass


def gen_dummydata_messages():
    """
    Fill dummy data for messages table.
    """
    pass


def gen_dummydata_payment_methods():
    """
    Fill dummy data for payment_methods table.
    """
    pass


def gen_dummydata_credit_cards():
    """
    Fill dummy data for credit_cards table.
    """
    pass


def gen_dummydata_paypal():
    """
    Fill dummy data for paypal table.
    """
    pass


def gen_dummydata_payout_accounts():
    """
    Fill dummy data for payout_accounts table.
    """
    pass


def gen_dummydata_payouts():
    """
    Fill dummy data for payouts table.
    """
    pass


def gen_dummydata_notifications():
    """
    Fill dummy data for notifications table.
    """
    pass