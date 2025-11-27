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
from random import choice, choices, randint, shuffle, sample
import datetime
from pathlib import Path
import sys
from psycopg2 import sql
from typing import List
import string
import json

# ---------------------------------------------------------------------------
# Third-party / extra imports
# ---------------------------------------------------------------------------
import rstr
import pandas as pd


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
import src.db.sql_repo as sqlrepo
from src.db.utils.db_helpers import get_tbl_contents_as_str
from src.utils.logger import logger


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------
def _fetch_table_ids(tbl_name: str)-> List:
    # Open connection
    conn = db_connection()
    cur = conn.cursor()
    
    # Get Id column name
    cur.execute(sqlrepo.FETCH_ID_COLUMN_NAME, (tbl_name,))
    id_column_name = cur.fetchall()
    id_column_name = id_column_name[0][0] # Unpack list of tuples

    # Get ID's with ID colum name
    query = sql.SQL(sqlrepo.FETCH_IDS).format(
    col=sql.Identifier(id_column_name),
    tbl=sql.Identifier(tbl_name)
    )
    cur.execute(query)
    ids = cur.fetchall()
    ids = [item[0] for item in ids]  # Unpack list of tuples

    # Close connection
    conn.commit()
    conn.close()

    return ids

def _fetch_table_ids_where(tbl_name: str, where: str)-> List:
    # Open connection
    conn = db_connection()
    cur = conn.cursor()
    
    # Get Id column name
    cur.execute(sqlrepo.FETCH_ID_COLUMN_NAME, (tbl_name,))
    id_column_name = cur.fetchall()
    id_column_name = id_column_name[0][0] # Unpack list of tuples

    # Get ID's with ID colum name
    query = sql.SQL(sqlrepo.FETCH_IDS_WHERE).format(
    col=sql.Identifier(id_column_name),
    tbl=sql.Identifier(tbl_name),
    where=sql.SQL(where) 
    )
    cur.execute(query)
    ids = cur.fetchall()
    ids = [item[0] for item in ids]  # Unpack list of tuples

    # Close connection
    conn.commit()
    conn.close()

    return ids


def _random_string(n=8):
    return "".join(choice(string.ascii_letters + string.digits) for _ in range(n))

def _gen_rand_timestamp():
    delta_seconds = int((seeds.stop_timestamp - seeds.start_timestamp).total_seconds())
    rand_sec = randint(0, delta_seconds)
    ts = seeds.start_timestamp + datetime.timedelta(seconds=rand_sec)
    return ts.isoformat()

def _gen_dummy_json():
    json_thing = {
    "title": " ".join([
            choice(seeds.christmas_gibberish_words) for _ in range(randint(1,4))
            ]),
    "body": "You have a new notification.",
    "type": "info"
    }
    return json.dumps(json_thing)

# ---------------------------------------------------------------------------
# ACCOUNTS
# ---------------------------------------------------------------------------
def gen_dummydata_accounts():
    """
    Fill dummy data for accounts table.

    Returns:
        email_addresses, first_names, last_names, roles, timestamps
    """
    # first names
    first_names = []
    for _ in range(seeds.num_gen_dummydata):
        name = ""
        syllable_ammount = randint(seeds.fn_min_sylls, seeds.fn_max_sylls)
        for _ in range(syllable_ammount):
            name += choice(seeds.first_name_sylls)
        first_names.append(name)

    # last names
    last_names = []
    for _ in range(seeds.num_gen_dummydata):
        name = ""
        syllable_ammount = randint(seeds.ln_min_sylls, seeds.ln_max_sylls)
        for _ in range(syllable_ammount):
            name += choice(seeds.last_name_sylls)
        last_names.append(name)

    # email addresses
    emails = []
    counter = 0
    while counter < seeds.num_gen_dummydata:
        email_address = (
            first_names[counter]
            + "."
            + last_names[counter]
            + "@"
            + choice(seeds.email_domains)
        )
        if email_address not in emails:
            emails.append(email_address)
            counter += 1
        else:
            continue

    # timestamps
    timestamps = []
    for _ in range(seeds.num_gen_dummydata):
        timestamps.append(_gen_rand_timestamp())

    # roles
    roles = []
    for _ in range(seeds.num_gen_dummydata - seeds.admin_count):
        roles.append(choice(["guest", "host"]))
    for _ in range(seeds.admin_count):
        roles.append("admin")

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('accounts'))
    cur.execute(query)
    data = zip(emails, first_names, last_names, roles, timestamps)
    cur.executemany(sqlrepo.INSERT_ACCOUNTS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into accounts table:")
    logger.info(get_tbl_contents_as_str('accounts'))

    # Return for later use
    return emails, first_names, last_names, roles, timestamps

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
    for _ in range(seeds.num_gen_dummydata):
        password = "".join(
            choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()",
                k=seeds.pwd_hash_length,
            )
        )
        password_hash.append(password)

    # timestamps
    password_updated_at = []
    for _ in range(seeds.num_gen_dummydata):
        password_updated_at.append(_gen_rand_timestamp())


    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('credentials'))
    cur.execute(query)
    
    # Get Id column name
    account_ids = _fetch_table_ids('accounts')

    # Create Data List
    data = zip(account_ids, password_hash, password_updated_at)
    cur.executemany(sqlrepo.INSERT_CREDENTIALS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into credentials table:")
    logger.info(get_tbl_contents_as_str('credentials'))

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
        city, postal = choice(list(seeds.city_postal.items()))
        country_name = seeds.city_country[city]
        street = choice(seeds.city_streets[city])
        house_number = str(randint(1, 200))

        # line1
        line1.append(f"{street} {house_number}")

        # optional line2
        if city in seeds.city_address_terms.keys():
            term1, term2 = seeds.city_address_terms[city]
            building_number = str(randint(1, 10))
            unit_number = str(randint(1, 50))
            line2.append(f"{term1} {building_number}, {term2} {unit_number}")

        cities.append(city)
        postal_code.append(postal)
        countries.append(country_name)

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('addresses'))
    cur.execute(query)
    data = zip(line1, line2, cities, postal_code, countries)
    cur.executemany(sqlrepo.INSERT_ADDRESSES, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into addresses table:")
    logger.info(get_tbl_contents_as_str('addresses'))

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

    # host_account_id
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('accommodations'))
    cur.execute(query)
    
    # Get Id column name from accounts table
    cur.execute(sqlrepo.FETCH_ID_COLUMN_NAME, ('accounts',))
    id_column_name = cur.fetchall()
    id_column_name = id_column_name[0][0] # Unpack list of tuples

    # Get ID's with ID colum name
    query = sql.SQL(sqlrepo.FETCH_HOST_IDS).format(
    col=sql.Identifier(id_column_name),
    tbl=sql.Identifier('accounts')
    )
    cur.execute(query)
    host_account_ids = cur.fetchall()
    host_account_ids = [item[0] for item in host_account_ids]  # Unpack list of tuples

    # Select a randwom host account id list matching num_gen_dummydata
    host_account_ids = [choice(host_account_ids) for _ in range(seeds.num_gen_dummydata)]

    # titles
    for _ in range(seeds.num_gen_dummydata):
        title = [
            choice(seeds.accomodation_title_words_dict["adjectives_general"]),
            choice(seeds.accomodation_title_words_dict["accommodation_nouns"]),
            choice(seeds.accomodation_title_words_dict["location_connectors"]),
            choice(seeds.accomodation_title_words_dict["adjectives_location"]),
            choice(seeds.accomodation_title_words_dict["place_names"]),
        ]
        titles.append(" ".join(title))
    
    # Get Id column name from addresses table
    address_ids = _fetch_table_ids('addresses')

    # prices
    for _ in range(seeds.num_gen_dummydata):
        price = randint(50, 500) * 100
        price_cents.append(price)

    # activity flags
    for _ in range(seeds.num_gen_dummydata):
        is_active.append(choice([True, False]))

    # created_at
    for _ in range(seeds.num_gen_dummydata):
        created_at.append(_gen_rand_timestamp())

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('accommodations'))
    cur.execute(query)
    data = zip(host_account_ids, titles, address_ids, price_cents, is_active, created_at)
    cur.executemany(sqlrepo.INSERT_ACCOMMODATIONS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into accommodations table:")
    logger.info(get_tbl_contents_as_str('accommodations'))

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

    for _ in range(seeds.num_gen_dummydata*4):  # More images than other tables
        # mime
        mime = choice(seeds.image_mimes)
        mimes.append(mime)

        # timestamp
        created_at.append(_gen_rand_timestamp())

        # storage key
        storage_key = "images/"
        storage_key += rstr.xeger(
            r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
        )
        storage_key += f".{mime.split('/')[1]}"
        storage_keys.append(storage_key)

    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('images'))
    cur.execute(query)
    data = zip(mimes, storage_keys, created_at)
    cur.executemany(sqlrepo.INSERT_IMAGES, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into images table:")
    logger.info(get_tbl_contents_as_str('images'))

    return mimes, storage_keys, created_at

# ---------------------------------------------------------------------------
# PAYMENT METHODS
# ---------------------------------------------------------------------------
def gen_dummydata_payment_methods():
    """
    Fill dummy data for payment_methods table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('payment_methods'))
    cur.execute(query)
    
    # Get account ids
    account_ids = _fetch_table_ids('accounts')

    # Create data list to insert later 
    data = [[],[],[]]

    # Create random ammount of payment methods per account
    for id in account_ids:
        payment_method_count = choice([1,2,3])
        method_types = ['card', 'paypal']
        methods_per_acc = [choice(method_types) for _ in range(payment_method_count)]
        for method in methods_per_acc:
            # Append all data
            data[0].append(id)
            data[1].append(method)
            data[2].append(_gen_rand_timestamp())

    # Finally insert the data
    if (len(data[0])== len(data[1]) and len(data[1]) == len(data[2])):
        data = zip(data[0], data[1], data[2])
        cur.executemany(sqlrepo.INSERT_PAYMENT_METHODS, data)
    else: print("gen_dummydata_payment_methods(): data has not euqal length")
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into payment_methods table:")
    logger.info(get_tbl_contents_as_str('payment_methods'))

def gen_dummydata_credit_cards():
    """
    Fill dummy data for credit_cards table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('credit_cards'))
    cur.execute(query)
    
    # Get Id column name
    card_ids = _fetch_table_ids_where(tbl_name='payment_methods', where="type = 'card'")
    brand = [choice(seeds.card_brands) for _ in card_ids]
    last4 = [randint(100,999) for _ in card_ids]
    exp_month = [randint(1,12) for _ in card_ids]
    exp_year = [randint(2023,2053) for _ in card_ids]
    
    # Zip data 
    data = zip(card_ids, brand, last4, exp_month, exp_year)

    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_CREDIT_CARDS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into credit_cards table:")
    logger.info(get_tbl_contents_as_str('credit_cards'))

def gen_dummydata_paypal():
    """
    Fill dummy data for paypal table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('paypal'))
    cur.execute(query)
    
    # Get Id column name
    paypal_ids = _fetch_table_ids_where(tbl_name='payment_methods', where="type = 'paypal'")
    paypal_user_id = [f"PP-{_random_string(n=8)}" for _ in paypal_ids]
    
    # email addresses
    emails = set()
    counter = 0
    while counter < len(paypal_ids):
        email_address = (
            "".join(choice(seeds.first_name_sylls) for _ in range(randint(1,3)))
            + "."
            + "".join(choice(seeds.last_name_sylls) for _ in range(randint(1,3)))
            + "@"
            + choice(seeds.email_domains)
        )
        if email_address not in emails:
            emails.add(email_address)
            counter += 1
        else:
            continue
    
    # Zip data 
    data = zip(paypal_ids, paypal_user_id, emails)

    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_PAYPAL, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into paypal table:")
    logger.info(get_tbl_contents_as_str('paypal'))

def gen_dummydata_reviews():
    """
    Fill dummy data for reviews table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('reviews'))
    cur.execute(query)
    
    # Get account ids
    accomodation_ids = _fetch_table_ids('accommodations')
    account_ids = _fetch_table_ids_where(tbl_name='accounts', where="role = 'guest'")

    accomodation = []  
    author = []
    rating = [] 
    description = [] 
    timestamp = [] 

    for _ in range(seeds.num_gen_dummydata*2):
        
        def gen_description(bad=True):
            sentiment = 'negative' if bad else 'positive'
            o = seeds.christmas_accommodation_reviews
            description = (
                f"{choice(o['openings'][sentiment])}! "
                f"{choice(o['accommodation_features'][sentiment])}. "
                f"{choice(o['intensifiers']).capitalize()}, "
                f"{choice(o['experiences'][sentiment])}. "
                f"{choice(o['connectors'])} "
                f"{choice(o['host_details'][sentiment])}. "
                f"{choice(o['random_details'])}. "
                f"{choice(o['comfort_ratings'][sentiment]).capitalize()}. "
                f"{choice(o['final_thoughts'][sentiment])}!"
            ) 
            return description
        
        accomodation.append(choice(accomodation_ids))
        rating.append(randint(1,5))
        author.append(choice(account_ids))
        if rating[-1] < 3:
            description.append(gen_description(bad=True))
        else:
            description.append(gen_description(bad=False))
        timestamp.append(_gen_rand_timestamp())
        
    # Zip data 
    data = zip(accomodation, author, rating, description, timestamp)

    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_REVIEWS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into reviews table:")
    logger.info(get_tbl_contents_as_str('reviews'))

def gen_dummydata_conversations():
    """
    Fill dummy data for conversations table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('conversations'))
    cur.execute(query)
    
    # Gen Data 
    data = [_gen_rand_timestamp() for _ in range(seeds.num_gen_dummydata)]
    data = zip(data)
    print(data)
    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_CONVERSATIONS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into conversations table:")
    logger.info(get_tbl_contents_as_str('conversations'))

def gen_dummydata_messages():
    """
    Fill dummy data for messages table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('messages'))
    cur.execute(query)
    
    # Get account ids
    conversation_ids = _fetch_table_ids('conversations')
    sender_id = []
    receiver_id = []
    conversation_id = []
    body = []
    is_read = []
    sent_at = []

    guest_ids = _fetch_table_ids_where(tbl_name='accounts', where="role = 'guest'")
    host_ids = _fetch_table_ids_where(tbl_name='accounts', where="role = 'host'")

    shuffle(host_ids)
    host_ids = host_ids[:int(len(host_ids)*0.7)]

    message_partners = []
    for conv_id in conversation_ids:
        message_partners.append((choice(host_ids), choice(guest_ids), conv_id))

    for partner in message_partners:
        conv_length = randint(1,15)
        start_time = datetime.datetime.fromisoformat(_gen_rand_timestamp())
        for i in range(conv_length):
            if i%2 == 0:
                sender_id.append(partner[0])
                receiver_id.append(partner[1])
            else:
                sender_id.append(partner[1])
                receiver_id.append(partner[0])
            conversation_id.append(partner[2])
            body.append(
                " ".join([
                choice(seeds.christmas_gibberish_words) for _ in range(randint(1,10))
                ]))
            is_read.append(True)
            sent_at.append(start_time)
            start_time += datetime.timedelta(minutes=randint(1,300))
        is_read[-1] = choice([True, False])

    # Zip data 
    data = zip(sender_id, receiver_id, conversation_id, body, sent_at, is_read)

    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_MESSAGES, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into messages table:")
    logger.info(get_tbl_contents_as_str('messages'))


def gen_dummydata_review_images():
    """
    Fill dummy data for review_images table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('review_images'))
    cur.execute(query)
    
    # Get account ids
    review_ids = _fetch_table_ids('reviews')
    image_ids = _fetch_table_ids('images')

    image_id = []
    review_id = []
    shuffle(image_ids)
    available = set(image_ids)
    for rid in review_ids[: len(review_ids)//2]:
        n = randint(1, 3)
        # stop if not enough images left
        if len(available) < n:
            break
        chosen = sample(list(available), n)  # unique
        for img in chosen:
            review_id.append(rid)
            image_id.append(img)
            available.remove(img)

    # Zip data 
    data = zip(review_id, image_id)

    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_REVIEW_IMAGES, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into review_images table:")
    logger.info(get_tbl_contents_as_str('review_images'))

def gen_dummydata_accommodation_images():
    """
    Fill dummy data for bookings table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('accommodation_images'))
    cur.execute(query)
    
    # Get account ids
    query = sqlrepo.FETCH_IMG_ID_FROM_REVIEW_IMGS
    cur.execute(query)
    review_img_ids = cur.fetchall()
    image_ids = _fetch_table_ids('images')
    accomodation_ids = _fetch_table_ids('accommodations')
    available = [x for x in image_ids if x not in review_img_ids]

    accommodation_id = []
    image_id = []
    sort_order = []
    is_cover = []
    caption = []
    room_tag = []

    for img in available:
        accommodation_id.append(choice(accomodation_ids))
        image_id.append(img) 
        sort_order.append(randint(1,8)) 
        is_cover.append(choice([True, False])) 
        caption.append(
                " ".join([
                choice(seeds.christmas_gibberish_words) for _ in range(randint(1,4))
                ]))
        room_tag.append(choice(seeds.room_tags)) 
        
    
            
    # Zip data 
    data = zip(accommodation_id, image_id, sort_order, is_cover, caption, room_tag)

    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_ACCOMMODATION_IMAGES, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into accommodation_images table:")
    logger.info(get_tbl_contents_as_str('accommodation_images'))


def gen_dummydata_notifications():
    """
    Fill dummy data for notifications table.
    """
    # Insert data into SQL table
    conn = db_connection()
    cur = conn.cursor()

    # Clear existing data
    query = sql.SQL(sqlrepo.DROP_ALL_TABLE_DATA).format(sql.Identifier('notifications'))
    cur.execute(query)
    
    # Get account ids
    account_ids = _fetch_table_ids('accounts')

    account_id = []
    payload = []
    sent_at = []

    for _ in range(seeds.num_gen_dummydata):
        account_id.append(choice(account_ids))
        payload.append(_gen_dummy_json())
        sent_at.append(_gen_rand_timestamp())

    # Zip data 
    data = zip(account_id, payload, sent_at)

    # Finally insert the data
    cur.executemany(sqlrepo.INSERT_NOTIFICATIONS, data)
    conn.commit()
    conn.close()

    # Test and log
    logger.info("Sample data inserted into notifications table:")
    logger.info(get_tbl_contents_as_str('notifications'))
"""
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(id),
    payload JSON,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
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





#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=



gen_dummydata_accounts()
gen_dummydata_credentials()
gen_dummydata_addresses()
gen_dummydata_accommodations()
gen_dummydata_images()
gen_dummydata_payment_methods()
gen_dummydata_credit_cards()
gen_dummydata_paypal()
gen_dummydata_reviews()
gen_dummydata_conversations()
gen_dummydata_messages()
gen_dummydata_review_images()
gen_dummydata_accommodation_images()
gen_dummydata_notifications()

get_tbl_contents_as_str('accounts')
get_tbl_contents_as_str('credentials')
get_tbl_contents_as_str('addresses')
get_tbl_contents_as_str('accommodations')
get_tbl_contents_as_str('images')
get_tbl_contents_as_str('payment_methods')
get_tbl_contents_as_str('credit_cards')
get_tbl_contents_as_str('paypal')
get_tbl_contents_as_str('reviews')
get_tbl_contents_as_str('conversations')
get_tbl_contents_as_str('messages')
get_tbl_contents_as_str('review_images')
get_tbl_contents_as_str('accommodation_images')
get_tbl_contents_as_str('notifications')

conn = db_connection()
cur = conn.cursor()

query = """
SELECT *
FROM accommodation_images
ORDER BY accommodation_id;
"""
cur.execute(query)

result = cur.fetchall()
df = pd.DataFrame(result)

print(df.to_string())
print(len(df[1]) == len(set(df[1])))

conn.close()