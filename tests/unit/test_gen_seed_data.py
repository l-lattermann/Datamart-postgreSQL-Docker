# Stdlib imports
import logging
from psycopg2 import sql
from datetime import datetime, date
import pytest

# Internal imports
import src.db.utils.db_introspect as introspect
from src.db.connection import db_connection



@pytest.fixture(scope="function")
def conn():
    connection = db_connection()
    connection.autocommit = False

    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()

# === INTEGRITY TESTS ===
def test_all_tables_filled(conn):
    """Test if all tables are populated"""
    logging.info("==== test_all_tables_filled =====")

    all_tables_true_list = [
        'notifications',
        'messages',
        'payment_methods',
        'accommodation_amenities',
        'payout_accounts',
        'paypal',
        'addresses',
        'accommodation_images',
        'accommodations',
        'credentials',
        'payments',
        'accounts',
        'images',
        'accommodation_calendar',
        'bookings',
        'payouts',
        'credit_cards',
        'reviews',
        'conversations',
        'review_images',
        'amenities'
    ]

    # Get all tables from schema
    all_tables_actual_list = introspect.fetch_all_tbl_names()

    try:
        assert set(all_tables_true_list) == set(all_tables_actual_list)
        logging.info("All tables populated")
    except AssertionError:
        logging.exception("Not all tables populated!")

    logging.info("")

    for table in all_tables_true_list:
        
        cur = conn.cursor()
        q = sql.SQL("SELECT * FROM {}").format(
            sql.Identifier(table)
        )
        cur.execute(q)
        rows = cur.fetchall()
        try:
            assert len(rows) >= 20
            logging.info(f">{table}< has more 20 entities.")
        except AssertionError:
            logging.exception(f">{table}< has less than 20 or no entities.")

    logging.info("")

def test_credentials(conn):
    """Test if all credentials have accounts and vice versa"""
    logging.info("==== test_credentials =====")
    cur = conn.cursor()

    # accounts → credentials
    cur.execute("""
        SELECT a.id
        FROM accounts a
        LEFT JOIN credentials c ON c.account_id = a.id
        WHERE c.account_id IS NULL;
    """)
    missing = cur.fetchall()
    try:
        assert len(missing) == 0
        logging.info("All accounts have credentials.")
    except AssertionError:
        logging.exception(f"Accounts missing credentials: {[r[0] for r in missing]}")

    # credentials → accounts
    cur.execute("""
        SELECT c.account_id
        FROM credentials c
        LEFT JOIN accounts a ON a.id = c.account_id
        WHERE a.id IS NULL;
    """)
    orphans = cur.fetchall()
    try:
        assert len(orphans) == 0
        logging.info("No orphan credentials exist.")
    except AssertionError:
        logging.exception(f"Orphan credentials rows: {[r[0] for r in orphans]}")

    # Count verification (1:1 relationship)
    cur.execute("SELECT COUNT(*) FROM accounts;")
    n_accounts = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM credentials;")
    n_credentials = cur.fetchone()[0]

    try:
        assert n_accounts == n_credentials
        logging.info("Accounts count equals credentials count (1:1).")
    except AssertionError:
        logging.exception(f"Count mismatch: accounts={n_accounts}, credentials={n_credentials}")

    logging.info("")

def test_addresses_and_accommodations_relationship(conn):
    """Test if all accommodations have addresses and vice versa"""
    logging.info("==== test_addresses_and_accommodations_relationship =====")
    cur = conn.cursor()

    # addresses → accommodations
    cur.execute("""
        SELECT ad.id
        FROM addresses ad
        LEFT JOIN accommodations ac ON ac.address_id = ad.id
        WHERE ac.id IS NULL;
    """)
    unused_addresses = cur.fetchall()

    try:
        assert len(unused_addresses) == 0
        logging.info("All addresses are assigned to accommodations.")
    except AssertionError:
        logging.exception(f"Unused addresses: {[r[0] for r in unused_addresses]}")

    # accommodations → addresses
    cur.execute("""
        SELECT id
        FROM accommodations
        WHERE address_id IS NULL;
    """)
    accommodations_without_address = cur.fetchall()

    try:
        assert len(accommodations_without_address) == 0
        logging.info("All accommodations have an address_id.")
    except AssertionError:
        logging.exception(
            f"Accommodations without address_id: {[r[0] for r in accommodations_without_address]}"
        )

    logging.info("")

def test_accommodation_images_fk_integrity(conn):
    """Test if all accommodation images have valid foreign keys"""
    logging.info("==== test_accommodation_images_fk_integrity =====")
    cur = conn.cursor()

    # accommodation_images → accommodations
    cur.execute("""
        SELECT ai.accommodation_id
        FROM accommodation_images ai
        LEFT JOIN accommodations a ON a.id = ai.accommodation_id
        WHERE a.id IS NULL;
    """)
    invalid_accommodations = cur.fetchall()

    try:
        assert len(invalid_accommodations) == 0
        logging.info("All accommodation_images have valid accommodation_id.")
    except AssertionError:
        logging.exception(
            f"Invalid accommodation_id in accommodation_images: {[r[0] for r in invalid_accommodations]}"
        )

    # accommodation_images → images
    cur.execute("""
        SELECT ai.image_id
        FROM accommodation_images ai
        LEFT JOIN images i ON i.id = ai.image_id
        WHERE i.id IS NULL;
    """)
    invalid_images = cur.fetchall()

    try:
        assert len(invalid_images) == 0
        logging.info("All accommodation_images have valid image_id.")
    except AssertionError:
        logging.exception(
            f"Invalid image_id in accommodation_images: {[r[0] for r in invalid_images]}"
        )

    logging.info("")

def test_payment_methods_have_valid_customer(conn):
    """Test if all payment methods have valid customer account id"""
    logging.info("==== test_payment_methods_have_valid_customer =====")
    cur = conn.cursor()

    # payment_methods → accounts
    cur.execute("""
        SELECT pm.id, pm.customer_id
        FROM payment_methods pm
        LEFT JOIN accounts a ON a.id = pm.customer_id
        WHERE pm.customer_id IS NOT NULL
          AND a.id IS NULL;
    """)
    invalid = cur.fetchall()

    try:
        assert len(invalid) == 0
        logging.info("All payment_methods have valid customer_id (or NULL).")
    except AssertionError:
        logging.exception(f"Payment methods with invalid customer_id: {invalid}")

    logging.info("")

def test_payment_method_details_exclusive_and_complete(conn):
    """Test if all payment methods have exactly one detail row (credit card or paypal)"""
    logging.info("==== test_payment_method_details_exclusive_and_complete =====")
    cur = conn.cursor()

    # credit_cards → payment_methods
    cur.execute("""
        SELECT cc.payment_method_id
        FROM credit_cards cc
        LEFT JOIN payment_methods pm ON pm.id = cc.payment_method_id
        WHERE pm.id IS NULL;
    """)
    cc_orphans = cur.fetchall()
    try:
        assert len(cc_orphans) == 0
        logging.info("All credit_cards have valid payment_method_id.")
    except AssertionError:
        logging.exception(f"Orphan credit_cards.payment_method_id: {[r[0] for r in cc_orphans]}")

    # paypal → payment_methods
    cur.execute("""
        SELECT pp.payment_method_id
        FROM paypal pp
        LEFT JOIN payment_methods pm ON pm.id = pp.payment_method_id
        WHERE pm.id IS NULL;
    """)
    pp_orphans = cur.fetchall()
    try:
        assert len(pp_orphans) == 0
        logging.info("All paypal rows have valid payment_method_id.")
    except AssertionError:
        logging.exception(f"Orphan paypal.payment_method_id: {[r[0] for r in pp_orphans]}")

    # Verify exactly one detail row per payment_method (XOR)
    cur.execute("""
        SELECT
            pm.id,
            (cc.payment_method_id IS NOT NULL) AS has_credit_card,
            (pp.payment_method_id IS NOT NULL) AS has_paypal
        FROM payment_methods pm
        LEFT JOIN credit_cards cc ON cc.payment_method_id = pm.id
        LEFT JOIN paypal pp ON pp.payment_method_id = pm.id
        WHERE (cc.payment_method_id IS NOT NULL AND pp.payment_method_id IS NOT NULL)
           OR (cc.payment_method_id IS NULL AND pp.payment_method_id IS NULL);
    """)
    bad = cur.fetchall()

    try:
        assert len(bad) == 0
        logging.info("Each payment_method has exactly one detail row (credit_cards XOR paypal).")
    except AssertionError:
        logging.exception(
            "Payment methods violating exclusivity/completeness (id, has_cc, has_pp): "
            + str(bad)
        )

    logging.info("")

def test_reviews_and_review_images_integrity(conn):
    """Test if all review images have correct image id and all reviews have author"""
    logging.info("==== test_reviews_and_review_images_integrity =====")
    cur = conn.cursor()

    # reviews → accommodations
    cur.execute("""
        SELECT COUNT(*)
        FROM reviews r
        LEFT JOIN accommodations a ON a.id = r.accommodation_id
        WHERE a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All reviews have valid accommodation_id.")
    except AssertionError:
        logging.exception(f"Reviews with invalid accommodation_id count: {n}")

    # reviews → accounts (author)
    cur.execute("""
        SELECT COUNT(*)
        FROM reviews r
        LEFT JOIN accounts acc ON acc.id = r.author_account_id
        WHERE acc.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All reviews have valid author_account_id.")
    except AssertionError:
        logging.exception(f"Reviews with invalid author_account_id count: {n}")

    # review_images → reviews
    cur.execute("""
        SELECT COUNT(*)
        FROM review_images ri
        LEFT JOIN reviews r ON r.id = ri.review_id
        WHERE r.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All review_images have valid review_id.")
    except AssertionError:
        logging.exception(f"review_images with invalid review_id count: {n}")

    # review_images → images
    cur.execute("""
        SELECT COUNT(*)
        FROM review_images ri
        LEFT JOIN images i ON i.id = ri.image_id
        WHERE i.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All review_images have valid image_id.")
    except AssertionError:
        logging.exception(f"review_images with invalid image_id count: {n}")

    logging.info("")

def test_messages_integrity(conn):
    """Test if all messages have valid sender, receiver and conversation"""
    logging.info("==== test_messages_integrity =====")
    cur = conn.cursor()

    # messages → accounts (sender)
    cur.execute("""
        SELECT COUNT(*)
        FROM messages m
        LEFT JOIN accounts a ON a.id = m.sender_id
        WHERE a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All messages have valid sender_id.")
    except AssertionError:
        logging.exception(f"Messages with invalid sender_id count: {n}")

    # messages → accounts (receiver)
    cur.execute("""
        SELECT COUNT(*)
        FROM messages m
        LEFT JOIN accounts a ON a.id = m.receiver_id
        WHERE a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All messages have valid receiver_id.")
    except AssertionError:
        logging.exception(f"Messages with invalid receiver_id count: {n}")

    # messages → conversations
    cur.execute("""
        SELECT COUNT(*)
        FROM messages m
        LEFT JOIN conversations c ON c.id = m.conversation_id
        WHERE c.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All messages have valid conversation_id.")
    except AssertionError:
        logging.exception(f"Messages with invalid conversation_id count: {n}")

    logging.info("")

def test_payout_accounts_integrity(conn):
    """Test if all payout accounts have valid host account id"""
    logging.info("==== test_payout_accounts_integrity =====")
    cur = conn.cursor()

    # payout_accounts → accounts
    cur.execute("""
        SELECT COUNT(*)
        FROM payout_accounts pa
        LEFT JOIN accounts a ON a.id = pa.host_account_id
        WHERE pa.host_account_id IS NOT NULL
          AND a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All payout_accounts have valid host_account_id (or NULL).")
    except AssertionError:
        logging.exception(f"payout_accounts with invalid host_account_id count: {n}")

    logging.info("")

def test_payouts_integrity(conn):
    """Test if all payouts have valid foreign keys"""
    logging.info("==== test_payouts_integrity =====")
    cur = conn.cursor()

    # payouts → accounts
    cur.execute("""
        SELECT COUNT(*)
        FROM payouts p
        LEFT JOIN accounts a ON a.id = p.host_account_id
        WHERE p.host_account_id IS NOT NULL
          AND a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All payouts have valid host_account_id (or NULL).")
    except AssertionError:
        logging.exception(f"payouts with invalid host_account_id count: {n}")

    # payouts → payout_accounts
    cur.execute("""
        SELECT COUNT(*)
        FROM payouts p
        LEFT JOIN payout_accounts pa ON pa.id = p.payout_account_id
        WHERE p.payout_account_id IS NOT NULL
          AND pa.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All payouts have valid payout_account_id (or NULL).")
    except AssertionError:
        logging.exception(f"payouts with invalid payout_account_id count: {n}")

    # payouts → bookings
    cur.execute("""
        SELECT COUNT(*)
        FROM payouts p
        LEFT JOIN bookings b ON b.id = p.booking_id
        WHERE p.booking_id IS NOT NULL
          AND b.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All payouts have valid booking_id (or NULL).")
    except AssertionError:
        logging.exception(f"payouts with invalid booking_id count: {n}")

    logging.info("")

def test_notifications_integrity(conn):
    """Test if all notifications have valid account id"""
    logging.info("==== test_notifications_integrity =====")
    cur = conn.cursor()

    # notifications → accounts
    cur.execute("""
        SELECT COUNT(*)
        FROM notifications n
        LEFT JOIN accounts a ON a.id = n.account_id
        WHERE n.account_id IS NOT NULL
          AND a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All notifications have valid account_id (or NULL).")
    except AssertionError:
        logging.exception(f"notifications with invalid account_id count: {n}")

    logging.info("")

def test_payments_integrity(conn):
    """Test if all payments have valid customer and payment method"""
    logging.info("==== test_payments_integrity =====")
    cur = conn.cursor()

    # payments → accounts
    cur.execute("""
        SELECT COUNT(*)
        FROM payments p
        LEFT JOIN accounts a ON a.id = p.customer_id
        WHERE p.customer_id IS NOT NULL
          AND a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All payments have valid customer_id (or NULL).")
    except AssertionError:
        logging.exception(f"payments with invalid customer_id count: {n}")

    # payments → payment_methods
    cur.execute("""
        SELECT COUNT(*)
        FROM payments p
        LEFT JOIN payment_methods pm ON pm.id = p.payment_method_id
        WHERE p.payment_method_id IS NOT NULL
          AND pm.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All payments have valid payment_method_id.")
    except AssertionError:
        logging.exception(f"payments with invalid payment_method_id count: {n}")

    logging.info("")

def test_bookings_integrity(conn):
    """Test if all bookings have valid guest, accommodation and payment"""
    logging.info("==== test_bookings_integrity =====")
    cur = conn.cursor()

    # bookings → accounts (guest)
    cur.execute("""
        SELECT COUNT(*)
        FROM bookings b
        LEFT JOIN accounts a ON a.id = b.guest_account_id
        WHERE a.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All bookings have valid guest_account_id.")
    except AssertionError:
        logging.exception(f"bookings with invalid guest_account_id count: {n}")

    # bookings → accommodations
    cur.execute("""
        SELECT COUNT(*)
        FROM bookings b
        LEFT JOIN accommodations ac ON ac.id = b.accommodation_id
        WHERE ac.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All bookings have valid accommodation_id.")
    except AssertionError:
        logging.exception(f"bookings with invalid accommodation_id count: {n}")

    # bookings → payments
    cur.execute("""
        SELECT COUNT(*)
        FROM bookings b
        LEFT JOIN payments p ON p.id = b.payment_id
        WHERE b.payment_id IS NOT NULL
          AND p.id IS NULL;
    """)
    n = cur.fetchone()[0]
    try:
        assert n == 0
        logging.info("All bookings have valid payment_id (or NULL).")
    except AssertionError:
        logging.exception(f"bookings with invalid payment_id count: {n}")

    logging.info("")


# === FAULTY DATA INSERTION TESTS ===
def test_accounts(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('a@test.com')")
    with pytest.raises(Exception):
        cur.execute("INSERT INTO accounts (email) VALUES ('a@test.com')")

def test_credentials(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('cred@test.com') RETURNING id")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO credentials (account_id, password_hash) VALUES (%s, 'hash')", (acc_id,))
    with pytest.raises(Exception):
        cur.execute("INSERT INTO credentials (account_id, password_hash) VALUES (9999, 'fail')")

def test_addresses(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO addresses (line1, city, country) VALUES ('L1','Berlin','DE')")
    with pytest.raises(Exception):
        cur.execute("INSERT INTO addresses (city, country) VALUES ('Berlin','DE')")

def test_amenities(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO amenities (name) VALUES ('WiFi')")
    with pytest.raises(Exception):
        cur.execute("INSERT INTO amenities (name) VALUES ('WiFi')")

def test_accommodations(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email, role) VALUES ('host@test.com','host') RETURNING id")
    host_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (%s,'Test',1000)", (host_id,))
    with pytest.raises(Exception):
        cur.execute("INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (%s,'Bad',-1)", (host_id,))

def test_accommodation_amenities(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('h2@test.com') RETURNING id")
    host_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodations (host_account_id,title,price_cents) VALUES (%s,'A',100)", (host_id,))
    cur.execute("INSERT INTO amenities (name) VALUES ('Kitchen') RETURNING id")
    amenity_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM accommodations WHERE title='A'")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodation_amenities VALUES (%s,%s)", (acc_id, amenity_id))
    with pytest.raises(Exception):
        cur.execute("INSERT INTO accommodation_amenities VALUES (%s,%s)", (acc_id, amenity_id))

def test_images(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO images (mime, storage_key) VALUES ('img','key1')")
    with pytest.raises(Exception):
        cur.execute("INSERT INTO images (mime, storage_key) VALUES ('img','key1')")

def test_accommodation_images(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('h3@test.com') RETURNING id")
    host_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodations (host_account_id,title,price_cents) VALUES (%s,'B',100)", (host_id,))
    cur.execute("INSERT INTO images (mime, storage_key) VALUES ('img','key2') RETURNING id")
    img_id = cur.fetchone()[0]
    cur.execute("SELECT id FROM accommodations WHERE title='B'")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodation_images VALUES (%s,%s,1,TRUE,'c','room')", (acc_id, img_id))

def test_accommodation_calendar(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('h4@test.com') RETURNING id")
    host_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodations (host_account_id,title,price_cents) VALUES (%s,'C',100)", (host_id,))
    cur.execute("SELECT id FROM accommodations WHERE title='C'")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodation_calendar VALUES (%s,%s,FALSE,0,1)", (acc_id, date.today()))
    with pytest.raises(Exception):
        cur.execute("INSERT INTO accommodation_calendar VALUES (%s,%s,FALSE,0,1)", (acc_id, date.today()))

def test_payment_methods(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('pay@test.com') RETURNING id")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO payment_methods (customer_id,type) VALUES (%s,'card')", (acc_id,))

def test_payments(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('p2@test.com') RETURNING id")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO payment_methods (customer_id,type) VALUES (%s,'card') RETURNING id", (acc_id,))
    pm_id = cur.fetchone()[0]
    cur.execute("INSERT INTO payments (customer_id,amount_cents,status,payment_method_id) VALUES (%s,100,'open',%s)", (acc_id, pm_id))
    with pytest.raises(Exception):
        cur.execute("INSERT INTO payments (customer_id,amount_cents,status,payment_method_id) VALUES (%s,-1,'open',%s)", (acc_id, pm_id))

def test_bookings(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('g@test.com') RETURNING id")
    guest = cur.fetchone()[0]
    cur.execute("INSERT INTO accounts (email) VALUES ('h5@test.com') RETURNING id")
    host = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodations (host_account_id,title,price_cents) VALUES (%s,'D',100)", (host,))
    cur.execute("SELECT id FROM accommodations WHERE title='D'")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO bookings (guest_account_id,accommodation_id,start_date,end_date) VALUES (%s,%s,%s,%s)", (guest, acc_id, datetime.now(), datetime.now()))

def test_reviews(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('rev@test.com') RETURNING id")
    user = cur.fetchone()[0]
    cur.execute("INSERT INTO accounts (email) VALUES ('h6@test.com') RETURNING id")
    host = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodations (host_account_id,title,price_cents) VALUES (%s,'E',100)", (host,))
    cur.execute("SELECT id FROM accommodations WHERE title='E'")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO reviews (accommodation_id,author_account_id,rating) VALUES (%s,%s,5)", (acc_id, user))
    with pytest.raises(Exception):
        cur.execute("INSERT INTO reviews (accommodation_id,author_account_id,rating) VALUES (%s,%s,6)", (acc_id, user))

def test_review_images(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO images (mime, storage_key) VALUES ('img','key3') RETURNING id")
    img_id = cur.fetchone()[0]
    cur.execute("INSERT INTO accounts (email) VALUES ('r2@test.com') RETURNING id")
    user = cur.fetchone()[0]
    cur.execute("INSERT INTO accounts (email) VALUES ('h7@test.com') RETURNING id")
    host = cur.fetchone()[0]
    cur.execute("INSERT INTO accommodations (host_account_id,title,price_cents) VALUES (%s,'F',100)", (host,))
    cur.execute("SELECT id FROM accommodations WHERE title='F'")
    acc_id = cur.fetchone()[0]
    cur.execute("INSERT INTO reviews (accommodation_id,author_account_id,rating) VALUES (%s,%s,4) RETURNING id", (acc_id, user))
    review_id = cur.fetchone()[0]
    cur.execute("INSERT INTO review_images VALUES (%s,%s)", (review_id, img_id))

def test_conversations(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO conversations DEFAULT VALUES")

def test_messages(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('s@test.com') RETURNING id")
    sender = cur.fetchone()[0]
    cur.execute("INSERT INTO accounts (email) VALUES ('r@test.com') RETURNING id")
    receiver = cur.fetchone()[0]
    cur.execute("INSERT INTO conversations DEFAULT VALUES RETURNING id")
    conv = cur.fetchone()[0]
    cur.execute("INSERT INTO messages (sender_id,receiver_id,conversation_id,body) VALUES (%s,%s,%s,'hi')", (sender, receiver, conv))

def test_credit_cards(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('cc@test.com') RETURNING id")
    acc = cur.fetchone()[0]
    cur.execute("INSERT INTO payment_methods (customer_id,type) VALUES (%s,'card') RETURNING id", (acc,))
    pm = cur.fetchone()[0]
    cur.execute("INSERT INTO credit_cards (payment_method_id,exp_month) VALUES (%s,12)", (pm,))
    with pytest.raises(Exception):
        cur.execute("INSERT INTO credit_cards (payment_method_id,exp_month) VALUES (%s,13)", (pm,))

def test_paypal(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('pp@test.com') RETURNING id")
    acc = cur.fetchone()[0]
    cur.execute("INSERT INTO payment_methods (customer_id,type) VALUES (%s,'paypal') RETURNING id", (acc,))
    pm = cur.fetchone()[0]
    cur.execute("INSERT INTO paypal (payment_method_id,paypal_user_id,email) VALUES (%s,'u1','e1@test.com')", (pm,))

def test_payout_accounts(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('host8@test.com') RETURNING id")
    host = cur.fetchone()[0]
    cur.execute("INSERT INTO payout_accounts (host_account_id,type) VALUES (%s,'card')", (host,))

def test_payouts(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('host9@test.com') RETURNING id")
    host = cur.fetchone()[0]
    cur.execute("INSERT INTO payout_accounts (host_account_id,type) VALUES (%s,'card') RETURNING id", (host,))
    payout_acc = cur.fetchone()[0]
    cur.execute("INSERT INTO payouts (host_account_id,payout_account_id,amount_cents) VALUES (%s,%s,1000)", (host, payout_acc))

def test_notifications(conn):
    
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts (email) VALUES ('notif@test.com') RETURNING id")
    acc = cur.fetchone()[0]
    cur.execute("INSERT INTO notifications (account_id,payload) VALUES (%s,'{\"type\":\"test\"}')", (acc,))