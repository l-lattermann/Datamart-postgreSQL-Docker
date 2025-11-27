"""
sql_repo.py

Central store for SQL statements used by DB utilities.

Principles:
- Keep introspection queries generic and based on information_schema.
- Do NOT format identifiers with f-strings; use psycopg2.sql.
- For tables with auto-increment IDs, omit the id column in INSERTs.
"""

# ============================================================================
# 1. Introspection queries
# ============================================================================

FETCH_ALL_TABLE_NAMES = """
    SELECT DISTINCT table_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name;
"""

FETCH_TABLE_METADATA = """
    SELECT
        column_name,
        data_type,
        is_nullable,
        column_default
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = %s
    ORDER BY ordinal_position;
"""

FETCH_TABLE_COLUMNS = """
    SELECT
        column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = %s
    ORDER BY ordinal_position;
"""

DUMP_TABLE = """
    SELECT *
    FROM {};
"""

# ============================================================================
# 2. Drop all data from a specific table
# ============================================================================
DROP_ALL_TABLE_DATA = """
    TRUNCATE TABLE {}     
    RESTART IDENTITY 
    CASCADE;
"""

# ============================================================================
# 2. Retrieve ID column name
# ============================================================================
FETCH_ID_COLUMN_NAME = """
    SELECT a.attname
    FROM pg_index i, pg_attribute a
    WHERE a.attrelid = i.indrelid
    AND a.attnum = ANY(i.indkey)
    AND i.indrelid = %s::regclass
    AND i.indisprimary;
"""

# ============================================================================
# 3. Retrieve ID's
# ============================================================================
FETCH_IDS = """
    SELECT {col}
    FROM {tbl}
    """

# ============================================================================
# 4. Retrieve host account ID's
# ============================================================================
FETCH_HOST_IDS = """
    SELECT {col}
    FROM {tbl}
    WHERE role = 'host';
    """

# ============================================================================
# 5. Retrieve table ID's with where condition
# ============================================================================
FETCH_IDS_WHERE = """
    SELECT {col}
    FROM {tbl}
    WHERE {where};
    """
FETCH_IMG_ID_FROM_REVIEW_IMGS = """
    SELECT image_id
    FROM review_images
    """
# ============================================================================
# 6. Table-specific INSERT templates (without ID columns)
# ============================================================================

INSERT_PAYOUT_ACCOUNTS = """
    INSERT INTO payout_accounts (host_account_id, type, is_default)
    VALUES (%s, %s, %s);
"""

INSERT_IMAGES = """
    INSERT INTO images (mime, storage_key, created_at)
    VALUES (%s, %s, %s);
"""

INSERT_ACCOMMODATION_AMENITIES = """
    INSERT INTO accommodation_amenities (accommodation_id, amenity_id)
    VALUES (%s, %s);
"""

INSERT_BOOKINGS = """
    INSERT INTO bookings (
        guest_account_id,
        accommodation_id,
        start_date,
        end_date,
        payment_id,
        status,
        created_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

INSERT_ACCOMMODATION_CALENDAR = """
    INSERT INTO accommodation_calendar (
        accommodation_id,
        day,
        is_blocked,
        price_cents,
        min_nights
    )
    VALUES (%s, %s, %s, %s, %s);
"""

INSERT_CONVERSATIONS = """
    INSERT INTO conversations (created_at)
    VALUES (%s);
"""

INSERT_ADDRESSES = """
    INSERT INTO addresses (line1, line2, city, postal_code, country)
    VALUES (%s, %s, %s, %s, %s);
"""

INSERT_NOTIFICATIONS = """
    INSERT INTO notifications (account_id, payload, sent_at)
    VALUES (%s, %s, %s);
"""

INSERT_CREDIT_CARDS = """
    INSERT INTO credit_cards (
        payment_method_id,
        brand,
        last4,
        exp_month,
        exp_year
    )
    VALUES (%s, %s, %s, %s, %s);
"""

INSERT_ACCOMMODATION_IMAGES = """
    INSERT INTO accommodation_images (
        accommodation_id,
        image_id,
        sort_order,
        is_cover,
        caption,
        room_tag
    )
    VALUES (%s, %s, %s, %s, %s, %s);
"""

INSERT_PAYMENTS = """
    INSERT INTO payments (
        customer_id,
        amount_cents,
        status,
        payment_method_id
    )
    VALUES (%s, %s, %s, %s);
"""

INSERT_CREDENTIALS = """
    INSERT INTO credentials (account_id, password_hash, password_updated_at)
    VALUES (%s, %s, %s);
"""

INSERT_ACCOUNTS = """
    INSERT INTO accounts (email, first_name, last_name, role, created_at)
    VALUES (%s, %s, %s, %s, %s);
"""

INSERT_ACCOMMODATIONS = """
    INSERT INTO accommodations (
        host_account_id,
        title,
        address_id,
        price_cents,
        is_active,
        created_at
    )
    VALUES (%s, %s, %s, %s, %s, %s);
"""

INSERT_PAYOUTS = """
    INSERT INTO payouts (
        host_account_id,
        payout_account_id,
        booking_id,
        amount_cents,
        currency,
        status
    )
    VALUES (%s, %s, %s, %s, %s, %s);
"""

INSERT_REVIEW_IMAGES = """
    INSERT INTO review_images (review_id, image_id)
    VALUES (%s, %s);
"""

INSERT_AMENITIES = """
    INSERT INTO amenities (name, category)
    VALUES (%s, %s);
"""

INSERT_REVIEWS = """
    INSERT INTO reviews (
        accommodation_id,
        author_account_id,
        rating,
        description,
        created_at
    )
    VALUES (%s, %s, %s, %s, %s);
"""

INSERT_PAYMENT_METHODS = """
    INSERT INTO payment_methods (customer_id, type, created_at)
    VALUES (%s, %s, %s);
"""

INSERT_MESSAGES = """
    INSERT INTO messages (
        sender_id,
        receiver_id,
        conversation_id,
        body,
        sent_at,
        is_read
    )
    VALUES (%s, %s, %s, %s, %s, %s);
"""

INSERT_PAYPAL = """
    INSERT INTO paypal (payment_method_id, paypal_user_id, email)
    VALUES (%s, %s, %s);
"""
