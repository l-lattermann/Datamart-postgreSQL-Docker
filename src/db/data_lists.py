"""
data_lists.py

Central seed/config module for dummy data generation.

Provides:
- global meta settings (row count, admin count, time window, password length)
- address/geography seed data (cities, streets, countries, address terms)
- person/account seed data (first/last name syllables, email domains)
- accommodation name generator words
- image-related seed data
- calendar horizon
"""


# META / GLOBAL SETTINGS
import datetime

# number of entries to create per table
num_gen_dummydata = 40

# number of admin accounts to reserve
admin_count = 3

# uniform timestamp window for all generators
start_timestamp = datetime.datetime(2022, 1, 1)
stop_timestamp = datetime.datetime(2025, 12, 31)

# length of generated password strings
pwd_hash_length = 32

"""
Target schema reminder (for mapping seeds → tables):

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


# GEO / ADDRESS DATA
# city → postal code
city_postal = {
    "snowflake village": "25DEC",
    "jinglebell junction": "12JOY",
    "candy cane creek": "31WIS",
    "frosty falls": "24CHE",
    "tinseltown": "01MER",
    "gingerbread grove": "25NOG",
    "mistletoe meadows": "12SLE",
    "reindeer ridge": "24PRE",
    "sugarplum springs": "25HOL",
    "winterberry woods": "12SNO",
}

# city → country
city_country = {
    "snowflake village": "north pole territories",
    "jinglebell junction": "winter wonderland",
    "candy cane creek": "gingerbread republic",
    "frosty falls": "snow globe federation",
    "tinseltown": "peppermint plains",
    "gingerbread grove": "cookie confederation",
    "mistletoe meadows": "evergreen empire",
    "reindeer ridge": "aurora borealis",
    "sugarplum springs": "frosting kingdom",
    "winterberry woods": "icicle isles",
}

# city → list of streets
city_streets = {
    "snowflake village": [
        "santa's sleigh way",
        "elf workshop lane",
        "rudolph boulevard",
        "hot cocoa drive",
        "snowball circle",
    ],
    "jinglebell junction": [
        "carol singers avenue",
        "ornament avenue",
        "wreath row",
        "holly berry street",
        "festive lights lane",
    ],
    "candy cane creek": [
        "peppermint twist",
        "gumdrop lane",
        "frosting boulevard",
        "sprinkles street",
        "marshmallow way",
    ],
    "frosty falls": ["snowman plaza", "icicle avenue", "frozen pond drive", "mittens lane", "scarf circle"],
    "tinseltown": ["glitter boulevard", "sparkle street", "shimmer avenue", "twinkle way", "ribbon road"],
    "gingerbread grove": ["cookie cutter lane", "frosting avenue", "cinnamon street", "nutmeg way", "molasses road"],
    "mistletoe meadows": ["kissing corner", "pine tree path", "yuletide boulevard", "evergreen street", "garland grove"],
    "reindeer ridge": ["dasher drive", "prancer plaza", "blitzen boulevard", "comet circle", "vixen valley"],
    "sugarplum springs": ["nutcracker avenue", "ballet boulevard", "fairy lights lane", "dream street", "magic way"],
    "winterberry woods": ["sledding hill", "ice skating circle", "snow fort lane", "toboggan trail", "igloo avenue"],
}

# city → (term for building, term for unit)
city_address_terms = {
    "snowflake village": ["cottage", "chimney"],
    "jinglebell junction": ["chalet", "hearth"],
    "candy cane creek": ["bakery", "door"],
    "frosty falls": ["cabin", "entrance"],
    "tinseltown": ["workshop", "gate"],
    "gingerbread grove": ["house", "window"],
    "mistletoe meadows": ["lodge", "porch"],
    "reindeer ridge": ["stable", "loft"],
    "sugarplum springs": ["palace", "chamber"],
    "winterberry woods": ["treehouse", "burrow"],
}


# PERSON / ACCOUNT SEEDS
# first-name building blocks
first_name_sylls = [
    "holly",
    "joy",
    "noel",
    "star",
    "snow",
    "angel",
    "frost",
    "candy",
    "merry",
    "belle",
    "nick",
    "ivy",
    "winter",
    "sparkle",
    "cookie",
    "ginger",
    "tinsel",
    "jolly",
    "frosty",
    "mistletoe",
    "rudolf",
    "blitzen",
    "carol",
    "crystal",
    "pine",
    "cinnamon",
    "pepper",
    "mint",
    "sugar",
    "claus",
]
fn_min_sylls, fn_max_sylls = 1, 1

# last-name building blocks
last_name_sylls = [
    "snow",
    "bell",
    "bright",
    "berry",
    "flake",
    "frost",
    "cheer",
    "light",
    "wish",
    "gift",
    "star",
    "wreath",
    "tree",
    "shine",
    "merry",
    "jingle",
    "sparkle",
    "twinkle",
    "cookie",
    "pudding",
    "mc",
    "the",
    "von",
    "claus",
]
ln_min_sylls, ln_max_sylls = 1, 3

# mail domains for identity generation
email_domains = [
    "northpolemail.com",
    "santasletter.net",
    "reindeerpost.org",
    "sleighmail.co",
    "wishlist.biz",
    "snowglobe.club",
    "elfmail.online",
    "gingerpost.lol",
    "festivebox.xyz",
]


# ACCOMMODATION NAME GENERATION
accomodation_title_words_dict = {
    # generic adjectives
    "adjectives_general": [
        "cozy",
        "magical",
        "enchanted",
        "frosty",
        "jolly",
        "twinkling",
        "merry",
        "whimsical",
        "snowy",
        "festive",
        "cheerful",
        "sparkly",
        "toasty",
        "delightful",
        "wonderous",
    ],
    # accommodation nouns
    "accommodation_nouns": [
        "cottage",
        "cabin",
        "chalet",
        "igloo",
        "lodge",
        "workshop",
        "gingerbread house",
        "snow palace",
        "treehouse",
        "sleigh station",
        "elf quarters",
        "winter retreat",
        "sugarplum suite",
        "cookie castle",
        "frost fortress",
    ],
    # connectors for "location" part
    "location_connectors": [
        "nestled in",
        "overlooking",
        "tucked away in",
        "perched above",
        "hidden within",
        "beside",
        "surrounded by",
        "at the edge of",
        "deep in",
        "right next to",
    ],
    # adjectives for locations
    "adjectives_location": [
        "snowy",
        "magical",
        "enchanted",
        "frosted",
        "glittering",
        "peaceful",
        "twinkling",
        "candlelit",
        "pristine",
        "sparkling",
        "silent",
        "starlit",
        "cozy",
        "mystical",
        "illuminated",
    ],
    # fun/fantasy place names
    "place_names": [
        "candy cane forest",
        "snowflake valley",
        "reindeer meadow",
        "gingerbread lane",
        "mistletoe mountain",
        "north pole",
        "sugarplum grove",
        "winter wonderland",
        "icicle creek",
        "holly hill",
        "tinsel woods",
        "ornament orchard",
        "peppermint peak",
        "jingle bell bay",
        "evergreen heights",
    ],
}


# IMAGE / MEDIA DATA
image_mimes = [
    "image/jpeg",
    "image/png",
    "image/webp",
]


# CALENDAR / AVAILABILITY
# how many days ahead to generate calendar entries
calendar_look_ahead = 365


# CREDIT CARD BRANDS
card_brands = [
    "Snowflake Express",
    "Frostcard",
    "Candy Cane Credit",
    "Winter Wondercard",
    "Jingle Bell Pay",
    "North Pole Club",
    "Reindeer Union",
    "Mistletoe Money",
]


# REVIEW SENTENCE BUILDING BLOCKS - CHRISTMAS CHAOS EDITION
christmas_accommodation_reviews = {
    "openings": {
        # Positive (70%)
        "positive": [
            "Holy jingle bells", "Sweet candy cane Jesus", "By Santa's glorious belly",
            "Absolute Christmas madness", "Peak holiday insanity", "Maximum festive chaos",
            "Chef's kiss from Mrs. Claus", "Rudolph's red nose couldn't guide me away",
            "My inner Grinch died here", "Christmas threw up here and I LOVED IT",
            "Elf-level enthusiasm achieved", "Mariah Carey would be proud",
            "More festive than Santa's browser history", "North Pole energy"
        ],
        # Negative (30%)
        "negative": [
            "Well, that was something", "Yikes on several bikes", "Big oof energy",
            "Not quite the vibe", "Slight Christmas crime scene", "Questionable life choices were made"
        ]
    },
    
    "accommodation_features": {
        "positive": [
            "The Christmas tree had more lights than a Vegas casino",
            "Decorations so aggressive my retinas filed a complaint",
            "Enough tinsel to strangle a small village",
            "The gingerbread smell was either wallpaper or a cry for help",
            "A fireplace that made me question if Santa was actually coming",
            "So many ornaments I thought I was in a Hobby Lobby explosion",
            "Hot cocoa station that would make Starbucks weep",
            "Fairy lights installed by someone on a sugar high",
            "A wreath so big it had its own gravitational pull",
            "The mistletoe was placed with aggressive intentions",
            "Stockings hung with concerning precision",
            "Candy canes in places candy canes should NOT be",
            "The nutcracker collection watched me with dead eyes",
            "Elf on the shelf positioned for maximum psychological damage"
        ],
        "negative": [
            "The Christmas tree looked like it had given up on life",
            "Decorations that screamed 'discount bin 2003'",
            "One (1) sad ornament doing its best",
            "Lights that flickered like a horror movie warning",
            "Fake snow that's definitely still in my suitcase",
            "A gingerbread house that violated health codes",
            "The tinsel was molting like a diseased peacock",
            "Decorations held up by spite and duct tape"
        ]
    },
    
    "experiences": {
        "positive": [
            "I made hot chocolate at 3am like a festive cryptid",
            "Watched so many Christmas movies I can now speak fluent Hallmark",
            "Had a one-person ugly sweater dance party",
            "Sang carols until the neighbors called the cops (worth it)",
            "Built a blanket fort that would make elves jealous",
            "Took enough photos to crash my phone twice",
            "Drank cocoa until I achieved enlightenment",
            "Wrote Santa a strongly worded letter of appreciation",
            "Did a full Mariah Carey concert for the shower drain",
            "Baked cookies while crying happy tears",
            "Had a snowball fight with myself (I won)",
            "Reached maximum cozy levels previously thought impossible"
        ],
        "negative": [
            "Got attacked by aggressive tinsel at 2am",
            "The Christmas music loop broke something in my brain",
            "Tripped over decorations more times than I'd like to admit",
            "Woke up with glitter in places glitter shouldn't go",
            "The animatronic Santa haunts my nightmares now",
            "Ate decorative candy and regretted my entire existence",
            "The constant jingling gave me stress-induced tinnitus"
        ]
    },
    
    "host_details": {
        "positive": [
            "Host left cookies and a note that said 'You're on the Nice List now'",
            "Host went full Santa cosplay for check-in (committed to the bit)",
            "Host provided emergency cookie dough (bless them)",
            "Host's Christmas spirit should be studied by scientists",
            "Host left reindeer slippers that changed my life",
            "Host included a laminated Christmas movie bingo card",
            "Host wrote personalized carol lyrics about my stay",
            "Host's tinsel budget must be astronomical",
            "Host decorated like their life depended on it",
            "Host left a care package that made me emotional"
        ],
        "negative": [
            "Host's elf surveillance system was concerning",
            "Host's idea of 'subtle festive touches' was a lie",
            "Host forgot to mention the motion-activated singing Santa",
            "Host left glitter bombs disguised as gifts",
            "Host's Christmas playlist was basically psychological warfare"
        ]
    },
    
    "random_details": [
        # Mix of absurd observations (neutral, can be used with any sentiment)
        "The bathroom had candy cane toilet paper (why though)",
        "Found tinsel in my breakfast somehow",
        "The WiFi password was HOHOHO123",
        "Every surface was sticky with holiday spirit (literally)",
        "The fridge was full of eggnog and questionable fruitcake",
        "Discovered a hidden stash of candy canes behind the couch",
        "The smoke detector was dressed as Rudolph",
        "Someone had bedazzled the thermostat",
        "Found a life-sized cardboard cutout of Mariah Carey in the closet",
        "The doorbell played 12 different versions of Jingle Bells",
        "Every switch had a tiny Santa hat on it",
        "The TV only played Christmas content (no joke)",
        "Someone put googly eyes on all the ornaments",
        "There was a framed photo of the host dressed as an elf"
    ],
    
    "comfort_ratings": {
        "positive": [
            "The bed was softer than Santa's beard",
            "Slept like a hibernating reindeer",
            "Blankets so cozy I entered a festive coma",
            "Pillows that dreams are made of (literally)",
            "Temperature control more perfect than the North Pole",
            "The couch consumed me in the best way",
            "Shower pressure strong enough to wash away my sins"
        ],
        "negative": [
            "The bed creaked Jingle Bells with every movement",
            "Heating was controlled by a possessed thermostat",
            "Couch looked better than it felt",
            "Too many decorative pillows - needed a degree to sit down",
            "The mattress was basically a decorative plank"
        ]
    },
    
    "final_thoughts": {
        "positive": [
            "Would sell my soul to come back",
            "Already planning next year's visit",
            "Ten out of ten jingle bells",
            "Highly recommend if you're clinically insane about Christmas",
            "Five stars and my eternal gratitude",
            "Worth every glitter-covered second",
            "Will haunt this place next Christmas like a festive ghost",
            "Book it before I do",
            "My therapist says I need to stop talking about it",
            "Chef's kiss from the North Pole",
            "Santa himself would approve this chaos"
        ],
        "negative": [
            "Four stars only because I'm still finding glitter",
            "Would return but with lower expectations",
            "Three stars - good but my therapist has concerns",
            "Recommend with heavy reservations",
            "Fun but I need a week to decompress",
            "Solid experience once the tinsel nightmares stop"
        ]
    },
    
    "intensifiers": [
        # Sprinkle these randomly for extra chaos
        "honestly", "legitimately", "no joke", "I kid you not", "surprisingly",
        "plot twist", "somehow", "inexplicably", "for some reason", "weirdly enough",
        "fun fact", "true story", "not gonna lie", "real talk", "hear me out"
    ],
    
    "connectors": [
        # Use these to link sentences
        "Also", "Plus", "Additionally", "Oh and", "Did I mention", "Fun fact:",
        "Side note:", "Important:", "Worth noting:", "Bonus:", "PS:", "Update:",
        "Quick note:", "Fair warning:", "Pro tip:", "Just saying:"
    ]
}

christmas_gibberish_words = [
    # Greetings
    "Ho ho", "Hey braw", "Morn gabba", "Jingle wang", "Festiv dok",
    "Holla bing", "Yule grook", "Merry blip", "Jolly wok", "Snowy hej",
    
    # Exclamations
    "Wida didlelidy", "Bingle bangle", "Tingle dangle", "Woop da loop",
    "Zingle zangle", "Frosty woosty", "Sparkle dorkle", "Jingle jangle",
    "Dingle dangle", "Wringle wrangle", "Tinkle tankle", "Boop da boop",
    
    # Verbs/Actions
    "na grek lok", "da fingle", "ba wringle", "go shnook", "ta bingle",
    "va crinkle", "ma wrinkle", "pa sprinkle", "ka dinkle", "la tingle",
    "sa mingle", "fa jingle", "wa dangle", "ra tangle", "ha mangle",
    
    # Nouns
    "the gloof", "ma snork", "da treeb", "ya flook", "the gringle",
    "ba wook", "na sprook", "ka flingle", "la crook", "the dook",
    "ma blook", "ya shnook", "da plook", "the grook", "ba floop",
    
    # Adjectives
    "verry zimmy", "much glonk", "so fribble", "mega crunk", "super dunk",
    "ultra plonk", "extra zonk", "really blunk", "quite shrimpy", "very cronky",
    "super flonky", "mega bonky", "ultra wonky", "pretty donky", "really stonky",
    
    # Questions
    "ya grok?", "na flek?", "da schmook?", "ba plek?", "ka glook?",
    "ma shprook?", "la frok?", "sa brok?", "ta gloop?", "wa plook?",
    
    # Festive nonsense
    "with da jingleflorp", "on the snorgleblop", "by ma cringleplop",
    "near ya flingleglop", "under ba dingleplop", "through ka wringleflop",
    "around la tingleblop", "behind ma springleplop", "inside ya cringleflop",
    
    # Random connectors
    "und", "aber", "also", "dann", "mit", "von", "zu", "bei", "nach",
    "vor", "uber", "durch", "ohne", "fur",
    
    # Time/when
    "toda schploop", "morra fleem", "later bloop", "soon ka doop",
    "now ma gleep", "tonight ya schleep", "tomorrow ba kreep",
    
    # Intensifiers
    "mega", "ultra", "super", "very", "much", "so", "extra", "really",
    "quite", "pretty", "totally", "fully", "completely",
    
    # Endings
    "ya know", "fo sho", "na mean", "ya feel", "ja ja", "nein nein",
    "okie dok", "roger dat", "got it", "kapish", "ya dig", "alrighty",
    
    # Christmas specific gibberish
    "Santalorp", "Elfy bork", "Reindy plork", "Snowy flurp", "Frosty murp",
    "Jolly durp", "Merry blurp", "Candy plonk", "Cocoa schlonk", "Cookie dronk",
    "Tinsel flink", "Wreath blink", "Tree plink", "Bell dink", "Star wink",
    
    # Punctuation words
    "bam", "pow", "whoosh", "zing", "boing", "pop", "click", "clack",
    "ding", "dong", "ring", "clang", "boom", "zap", "ping"
]

room_tags = [
    "reindeer-approved bedroom",
    "silent-night master suite",
    "gingerbread-scented guest room",
    "candy cane living room",
    "mistletoe lounge zone",
    "elf-sized kids room",
    "North Pole office corner",
    "hot cocoa kitchenette",
    "Santa’s snack-ready kitchen",
    "present-wrapping workstation",
    "sleigh-parking garage",
    "fireplace-worthy cozy lounge",
    "jingle bell dining area",
    "mulled-wine balcony",
    "snowflake-view rooftop terrace",
    "warm-socks reading nook",
    "chimney-friendly attic room",
    "cookie-baking laboratory (kitchen)"
]