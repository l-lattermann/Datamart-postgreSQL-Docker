# File to dynamicly generate generic table filler data 
import random
import datetime
import src.db.data_lists as seeds
import rstr

from src.db.connection import db_connection


def gen_dummydata_accounts():
    '''
    Function to fill dummy data into accounts table.
    Params: None
    Returns: email_adresses, first_names, last_names, roles, timestamps
    '''

    # Generate First Names
    first_names = []
    for dummy_id in range(seeds.num_gen_dummydata):
        name = ''
        syllable_ammount = random.randint(seeds.fn_min_sylls, seeds.fn_max_sylls)
        for _ in range(syllable_ammount):
            name += random.choice(seeds.first_name_syllables)
        first_names.append(name)
    
    # Generate Last Names
    last_names = []
    for dummy_id in range(seeds.num_gen_dummydata):
        name = ''
        syllable_ammount = random.randint(seeds.ln_min_sylls, seeds.ln_max_sylls)
        for _ in range(syllable_ammount):
            name += random.choice(seeds.last_name_syllables)
        last_names.append(name)

    # Generate Email Adresses
    email_adresses = []
    for dummy_id in range(seeds.num_gen_dummydata):
        email_adress = first_names[dummy_id] + '.' + last_names[dummy_id] + '@' + random.choice(seeds.email_domains)
        email_adresses.append(email_adress)

    # Generate timestamps
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    timestamps = []
    for dummy_id in range(seeds.num_gen_dummydata):
        random_time_step =  datetime.timedelta(seconds=random.randint(0, int(time_delta.total_seconds())))
        random_timestamp = seeds.start_timestamp + random_time_step
        timestamps.append(random_timestamp)
    
    # Generate roles
    roles = []
    for dummy_id in range(seeds.num_gen_dummydata-seeds.admin_count):
        roles.append(random.choice(['guest', 'host']))
    for dummy_id in range(seeds.admin_count):
        roles.append('admin')
    
    return email_adresses, first_names, last_names, roles, timestamps

    # Insert
def gen_dummydata_credentials():
    '''
    Function to fill dummy data into credentials table.
    Params: None
    Returns: password_hash, password_updated_at
    '''
    password_hash = []
    for dummy_id in range(seeds.num_gen_dummydata):
        password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()', k=seeds.pwd_hash_length))
        password_hash.append(password)

    # Generate timestamps
    password_updated_at = []
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    timestamps = []
    for dummy_id in range(seeds.num_gen_dummydata):
        random_time_step =  datetime.timedelta(seconds=random.randint(0, int(time_delta.total_seconds())))
        random_timestamp = seeds.start_timestamp + random_time_step
        timestamps.append(random_timestamp)
        password_updated_at.append(random_timestamp)

    return password_hash, password_updated_at

def gen_dummydata_addresses():
    '''
    Function to fill dummy data into addresses table.
    Params: None
    Returns: line1, line2, city, postal_code, country
    '''
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
        line1.append(f"{street} {house_number}")
        if city in seeds.city_address_terms.keys():
            term1, term2 = seeds.city_address_terms[city]
            building_number = str(random.randint(1, 10))
            unit_number = str(random.randint(1, 50))
            line2.append(f"{term1} {building_number}, {term2} {unit_number}")
        cities.append(city)
        postal_code.append(postal)
        countries.append(country_name)

    return line1, line2, cities, postal_code, countries

def gen_dummydata_accommodations():
    '''
    Function to fill dummy data into accommodations table.
    Params: None
    Returns: None
    '''
    titles = []
    price_cents = []
    is_active = []
    created_at = []
    # Generate accommodation titles
    for _ in range(seeds.num_gen_dummydata):
        title = [
            random.choice(seeds.accomodation_title_words_dict['adjectives_general']),
            random.choice(seeds.accomodation_title_words_dict['accommodation_nouns']),
            random.choice(seeds.accomodation_title_words_dict['location_connectors']),
            random.choice(seeds.accomodation_title_words_dict['adjectives_location']),
            random.choice(seeds.accomodation_title_words_dict['place_names']),
        ]
        titles.append(' '.join(title))
        print(title)
    # Generate price in cents
    for _ in range(seeds.num_gen_dummydata):
        price = random.randint(50, 500) * 100  # Price between 50.00 and 500.00
        price_cents.append(price)
    # Generate is_active status
    for _ in range(seeds.num_gen_dummydata):
        is_active.append(random.choice([True, False]))
    # Generate created_at timestamps
    time_delta = seeds.stop_timestamp - seeds.start_timestamp
    for _ in range(seeds.num_gen_dummydata):
        random_time_step =  datetime.timedelta(seconds=random.randint(0, int(time_delta.total_seconds())))
        random_timestamp = seeds.start_timestamp + random_time_step
        created_at.append(random_timestamp)
    return titles, price_cents, is_active, created_at

def gen_dummydata_images():
    '''
    Function to fill dummy data into images table.
    Params: None
    Returns: mime, storage_key, created_at
    '''
    mimes = []
    storage_keys = []
    created_at = []
    # Generate mime types and storage keys
    for _ in range(seeds.num_gen_dummydata):
        # Generate mime type
        mime = random.choice(seeds.image_mimes)
        mimes.append(mime)
        # Generate a random created_at timestamp
        time_delta = seeds.stop_timestamp - seeds.start_timestamp
        random_time_step =  datetime.timedelta(seconds=random.randint(0, int(time_delta.total_seconds())))
        random_timestamp = seeds.start_timestamp + random_time_step
        created_at.append(random_timestamp)
        # Generate a random storage key (e.g., UUID or random string)
        storage_key = "images/" 
        storage_key += rstr.xeger(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}')
        storage_key += f".{mime.split('/')[1]}"
        storage_keys.append(storage_key)
    return mimes, storage_keys, created_at

def gen_dummydata_accommodation_calendar():
    '''
    Function to fill dummy data into accommodation_calendar table.
    Params: None
    Returns: day, is_blocked, price_cents, min_nights
    '''
    days = []
    is_blocked = []
    price_cents = []
    min_nights = []
    # Generate calendar entries

    return days, is_blocked, price_cents, min_nights

def gen_dummydata_payments():
    '''
    Function to fill dummy data into payments table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_bookings():
    '''
    Function to fill dummy data into bookings table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_reviews():
    '''
    Function to fill dummy data into reviews table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_review_images():
    '''
    Function to fill dummy data into review_images table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_conversations():
    '''
    Function to fill dummy data into conversations table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_messages():
    '''
    Function to fill dummy data into messages table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_payment_methods():
    '''
    Function to fill dummy data into payment_methods table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_credit_cards():
    '''
    Function to fill dummy data into credit_cards table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_paypal():
    '''
    Function to fill dummy data into paypal table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_payout_accounts():
    '''
    Function to fill dummy data into payout_accounts table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_payouts():
    '''
    Function to fill dummy data into payouts table.
    Params: None
    Returns: None
    '''
    pass
def gen_dummydata_notifications():
    '''
    Function to fill dummy data into notifications table.
    Params: None
    Returns: None
    '''
    pass
