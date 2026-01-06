# Stdlib imports
import logging
from psycopg2 import sql

# Internal imports
import src.db.utils.db_introspect as introspect
from src.db.connection import db_connection  



def test_all_tables_filled():
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

    # Get all tables from shema
    all_tables_actual_list = introspect.fetch_all_tbl_names()

    try:
        assert set(all_tables_true_list) == set(all_tables_actual_list)
        logging.info("All tables populated")
    except AssertionError:
        logging.exception("Not all tables populated!")

    logging.info("")

    for table in all_tables_true_list:
        con = db_connection()
        cur = con.cursor()
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

    cur.close()
    con.close()
    logging.info("")

def test_credentials():
    """Test if all credentials have accounts and vice versa"""
    logging.info("==== test_credentials =====")

    con = db_connection()
    cur = con.cursor()

    # A) accounts without credentials
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

    # B) credentials without accounts (should be impossible with FK, but test anyway)
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

    # C) counts match (1:1 expected because credentials.account_id is PK)
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
    cur.close()
    con.close()

def test_addresses_and_accommodations_relationship():
    """Test if all accommodations have addresses and vice versa"""
    logging.info("==== test_addresses_and_accommodations_relationship =====")

    con = db_connection()
    cur = con.cursor()

    # A) addresses not referenced by any accommodation
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

    # B) accommodations without address
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
    cur.close()
    con.close()

def test_accommodation_images_fk_integrity():
    """Test if all accommodations images have addresses and vice versa"""
    logging.info("==== test_accommodation_images_fk_integrity =====")

    con = db_connection()
    cur = con.cursor()

    # A) invalid accommodation_id
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

    # B) invalid image_id
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
    cur.close()
    con.close()

def test_payment_methods_have_valid_customer():
    """Test if all payment methods have valid account id"""
    logging.info("==== test_payment_methods_have_valid_customer =====")

    con = db_connection()
    cur = con.cursor()

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
    cur.close()
    con.close()

def test_payment_method_details_exclusive_and_complete():
    """Test if all payment methods have valid cards or paypal"""
    logging.info("==== test_payment_method_details_exclusive_and_complete =====")

    con = db_connection()
    cur = con.cursor()

    # A) credit_cards orphan payment_method_id (should be impossible with FK, but test)
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

    # B) paypal orphan payment_method_id (should be impossible with FK, but test)
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

    # C) exactly one detail row per payment_method
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
    cur.close()
    con.close()

def test_reviews_and_review_images_integrity():
    """Test if all review images have coorect image id and all reviews hace author"""
    logging.info("==== test_reviews_and_review_images_integrity =====")

    con = db_connection()
    cur = con.cursor()

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
    cur.close()
    con.close()

def test_messages_integrity():
    """Test if all review images have coorect image id and all reviews hace author"""
    logging.info("==== test_messages_integrity =====")

    con = db_connection()
    cur = con.cursor()

    # sender exists
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

    # receiver exists
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

    # conversation exists
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
    cur.close()
    con.close()

def test_payout_accounts_integrity():
    """Test FK integrity for payout_accounts"""
    logging.info("==== test_payout_accounts_integrity =====")

    con = db_connection()
    cur = con.cursor()

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
    cur.close()
    con.close()

def test_payouts_integrity():
    """Test FK integrity for payouts"""
    logging.info("==== test_payouts_integrity =====")

    con = db_connection()
    cur = con.cursor()

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
    cur.close()
    con.close()

def test_notifications_integrity():
    """Test FK integrity for notifications"""
    logging.info("==== test_notifications_integrity =====")

    con = db_connection()
    cur = con.cursor()

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
    cur.close()
    con.close()

def test_payments_integrity():
    """Test FK integrity for payments"""
    logging.info("==== test_payments_integrity =====")

    con = db_connection()
    cur = con.cursor()

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
    cur.close()
    con.close()

def test_bookings_integrity():
    """Test FK integrity for bookings"""
    logging.info("==== test_bookings_integrity =====")

    con = db_connection()
    cur = con.cursor()

    # bookings → guest account
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

    cur.close()
    con.close()