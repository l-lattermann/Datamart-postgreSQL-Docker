# ============================================================
# META / GLOBAL SETTINGS
# ============================================================
import datetime

# Number of entries to create for each table
num_gen_dummydata = 40
admin_count = 3
start_timestamp = datetime.datetime(2022, 1, 1)
stop_timestamp = datetime.datetime(2025, 12, 31)
pwd_hash_length = 32

"""
addresses(id, line1, line2, city, postal_code, country)
amenities(id, name, category)
accommodations(id, host_account_id, title, address_id, price_cents, is_active, created_at)
accommodation_amenities(accommodation_id, amenity_id)
images(id, mime, storage_key, created_at)
accommodation_images(accommodation_id, image_id, sort_order, is_cover, caption, room_tag)
accommodation_calendar(accommodation_id, day, is_blocked, price_cents, min_nights)
payments(id, customer_id, amount_cents, status, payment_method_id)
bookings(id, guest_account_id, accommodation_id, start_date, end_date, payment_id, status, created_at)
reviews(id, accommodation_id, author_account_id, rating, description, created_at)
review_images(review_id, image_id)
conversations(id, created_at)
messages(id, sender_id, receiver_id, conversation_id, body, sent_at, is_read)
payment_methods(id, customer_id, type, created_at)
credit_cards(id, payment_method_id, brand, last4, exp_month, exp_year)
paypal(id, payment_method_id, paypal_user_id, email)
payout_accounts(id, host_account_id, type, is_default)
payouts(id, host_account_id, payout_account_id, booking_id, amount_cents, currency, status)
notifications(id, account_id, payload, sent_at)
"""

# ============================================================
# GEO / ADDRESS DATA
# ============================================================

# Postal code dictionary for some example cities in various countries
city_postal = {
    "berlin": "10115",          # Germany
    "paris": "75001",           # France
    "madrid": "28001",          # Spain
    "rome": "00184",            # Italy
    "amsterdam": "1012 WX",     # Netherlands
    "vienna": "1010",           # Austria
    "zurich": "8001",           # Switzerland
    "oslo": "0150",             # Norway
    "prague": "110 00",         # Czech Republic
    "copenhagen": "1050"        # Denmark
}

# Country dictionary for some example countries
city_country = {
    "berlin": "germany",
    "paris": "france",
    "madrid": "spain",
    "rome": "italy",
    "amsterdam": "netherlands",
    "vienna": "austria",
    "zurich": "switzerland",
    "oslo": "norway",
    "prague": "czech republic",
    "copenhagen": "denmark"
}

# Streets per city
city_streets = {
    "berlin": ["unter den linden", "friedrichstraße", "karl-marx-allee", "kurfürstendamm", "potsdamer platz"],
    "paris": ["rue de rivoli", "avenue des champs-élysées", "boulevard saint-germain", "rue mouffetard", "rue de la paix"],
    "madrid": ["gran vía", "calle de alcalá", "paseo del prado", "calle mayor", "plaza de españa"],
    "rome": ["via del corso", "via nazionale", "via condotti", "via veneto", "piazza navona"],
    "amsterdam": ["damrak", "kalverstraat", "leidsestraat", "prinsengracht", "herengracht"],
    "vienna": ["karntner straße", "mariahilfer straße", "graben", "ringstraße", "naschmarktgasse"],
    "zurich": ["bahnhofstrasse", "langstrasse", "niederdorfstrasse", "augustinergasse", "seefeldstrasse"],
    "oslo": ["karl johans gate", "bogstadveien", "torggata", "akersgata", "grünerløkka"],
    "prague": ["wenceslas square", "narodni trida", "parizska", "celetna", "vaclavske namesti"],
    "copenhagen": ["stroget", "nyhavn", "vestergade", "norrebrogade", "osterbrogade"]
}

# City-specific address terms
city_address_terms = {
    "berlin": ["wohnung", "haustür"],
    "paris": ["appartement", "porte"],
    "madrid": ["piso", "puerta"],
    "rome": ["scala", "interno"],
    "amsterdam": ["appartement", "verdieping"],
    "vienna": ["stiege", "tür"],
    "zurich": ["wohnung", "eingang"],
    "oslo": ["leilighet", "inngang"],
    "prague": ["byt", "vchod"],
    "copenhagen": ["lejlighed", "opgang"]
}

# ============================================================
# PERSON / ACCOUNT DUMMY DATA
# ============================================================

first_name_syllables = [
    "roxy", "lola", "ruby", "max", "cassie",
    "nina", "jett", "lexi", "vera", "trixie",
    "rico", "gigi", "zane", "luna", "dante",
    "cleo", "raven", "jade", "mila", "axel",
    "kai", "enzo", "finn", "jax", "ryder",
    "romeo", "blake", "luca", "troy", "asher"
]
fn_min_sylls, fn_max_sylls = 1, 1

last_name_syllables = [
    "wig", "gle", "pants", "snort", "ington", "bork", "fluff",
    "bottom", "sniff", "blaster", "face", "dozer", "puff",
    "tastrophe", "sauce", "smash", "nugget", "bucket",
    "snuggle", "muffin", "von", "mc", "the", "nator"
]
ln_min_sylls, ln_max_sylls = 1, 3

email_domains = [
    "spicyinbox.com",
    "luvmail.net",
    "winkhub.org",
    "afterdarkmail.co",
    "smoothoperator.biz",
    "cupidconnect.club",
    "hotbeans.online",
    "saucypigeon.lol",
    "midnightmsg.xyz"
]

# ============================================================
# ACCOMMODATION NAME GENERATION
# ============================================================
accomodation_title_words_dict = {

# adjectives for overall description
'adjectives_general' : [
    "deranged", "glorious", "crusty", "juicy", "feral",
    "moist", "sparkly", "delirious", "grumpy", "suspicious",
    "flamboyant", "chunky", "chaotic", "greasy", "magnificent"
],

# accommodation nouns
'accommodation_nouns' : [
    "shack", "palace", "dumpster", "lair", "bunker",
    "yurt", "situation", "compound", "crib", "shed",
    "mansion", "toilet", "dojo", "fortress", "nest"
],

# location connectors
'location_connectors' : [
    "in the middle of", "next to", "right behind", "under", "overlooking",
    "adjacent to", "across from", "beneath", "lost inside", "deep within"
],

# descriptive adjectives for locations
'adjectives_location' : [
    "cursed", "radioactive", "shady", "chaotic", "slippery",
    "fermented", "haunted", "illegal", "drippy", "glorious",
    "unholy", "sticky", "vibrating", "derelict", "spark-coated"
],

# funny or imaginary place names
'place_names' : [
    "yeet canyon", "dumpster lagoon", "boink mountain", "cringe valley", "snacc swamp",
    "bongo desert", "dripfield", "meme gulch", "goober bay", "fizzle hill",
    "sauce plains", "burp island", "blorb forest", "void beach", "chonk cliffs"
]
}

# ============================================================
# IMAGE DUMMY DATA
# ============================================================
image_mimes = [
    "image/jpeg",
    "image/png",
    "image/webp"
]

# ============================================================
# IMAGE DUMMY DATA
# ============================================================
calendar_look_ahead = 365