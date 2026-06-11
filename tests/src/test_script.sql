-- ============================================================
-- DBeaver Community SQL Test Suite
-- Run via: F3 (Open SQL Script) or paste into SQL Editor
-- Each block is self-contained and ROLLS BACK after execution
-- Use "Execute SQL Script" (Alt+X) to run all at once
-- ============================================================


-- ============================================================
-- === SECTION 1: INTEGRITY TESTS ===
-- ============================================================


-- ------------------------------------------------------------
-- TEST: test_all_tables_filled
-- Checks all 21 expected tables exist and have >= 20 rows
-- ------------------------------------------------------------
DO $$
DECLARE
    tbl TEXT;
    row_count INT;
    tables TEXT[] := ARRAY[
        'notifications','messages','payment_methods',
        'accommodation_amenities','payout_accounts','paypal',
        'addresses','accommodation_images','accommodations',
        'credentials','payments','accounts','images',
        'accommodation_calendar','bookings','payouts',
        'credit_cards','reviews','conversations',
        'review_images','amenities'
    ];
BEGIN
    RAISE NOTICE '==== test_all_tables_filled ====';

    -- Check all expected tables exist in the schema
    FOR i IN 1..array_length(tables, 1) LOOP
        tbl := tables[i];
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = tbl
        ) THEN
            EXECUTE format('SELECT COUNT(*) FROM %I', tbl) INTO row_count;
            IF row_count >= 20 THEN
                RAISE NOTICE 'PASS | Table: % | Row count: %', tbl, row_count;
            ELSE
                RAISE WARNING 'FAIL | Table: % | Only % rows (expected >= 20)', tbl, row_count;
            END IF;
        ELSE
            RAISE WARNING 'FAIL | Table: % | DOES NOT EXIST in schema', tbl;
        END IF;
    END LOOP;

    RAISE NOTICE '==== END test_all_tables_filled ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_credentials
-- Checks 1:1 relationship between accounts and credentials
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_credentials (integrity) ====';

    -- Accounts missing credentials
    SELECT COUNT(*) INTO n
    FROM accounts a
    LEFT JOIN credentials c ON c.account_id = a.id
    WHERE c.account_id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All accounts have credentials';
    ELSE
        RAISE WARNING 'FAIL | % account(s) missing credentials', n;
    END IF;

    -- Orphan credentials (no matching account)
    SELECT COUNT(*) INTO n
    FROM credentials c
    LEFT JOIN accounts a ON a.id = c.account_id
    WHERE a.id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | No orphan credentials exist';
    ELSE
        RAISE WARNING 'FAIL | % orphan credential row(s)', n;
    END IF;

    -- 1:1 count check
    DECLARE
        n_accounts INT;
        n_creds    INT;
    BEGIN
        SELECT COUNT(*) INTO n_accounts FROM accounts;
        SELECT COUNT(*) INTO n_creds    FROM credentials;
        IF n_accounts = n_creds THEN
            RAISE NOTICE 'PASS | accounts=% equals credentials=% (1:1)', n_accounts, n_creds;
        ELSE
            RAISE WARNING 'FAIL | accounts=% != credentials=% (not 1:1)', n_accounts, n_creds;
        END IF;
    END;

    RAISE NOTICE '==== END test_credentials (integrity) ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_addresses_and_accommodations_relationship
-- Every address maps to an accommodation and vice versa
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_addresses_and_accommodations_relationship ====';

    -- Unused addresses (no accommodation references them)
    SELECT COUNT(*) INTO n
    FROM addresses ad
    LEFT JOIN accommodations ac ON ac.address_id = ad.id
    WHERE ac.id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All addresses are assigned to an accommodation';
    ELSE
        RAISE WARNING 'FAIL | % address(es) not assigned to any accommodation', n;
    END IF;

    -- Accommodations without an address
    SELECT COUNT(*) INTO n
    FROM accommodations
    WHERE address_id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All accommodations have an address_id';
    ELSE
        RAISE WARNING 'FAIL | % accommodation(s) missing address_id', n;
    END IF;

    RAISE NOTICE '==== END test_addresses_and_accommodations_relationship ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_accommodation_images_fk_integrity
-- accommodation_images FK → accommodations and images
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_accommodation_images_fk_integrity ====';

    SELECT COUNT(*) INTO n
    FROM accommodation_images ai
    LEFT JOIN accommodations a ON a.id = ai.accommodation_id
    WHERE a.id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All accommodation_images have valid accommodation_id';
    ELSE
        RAISE WARNING 'FAIL | % row(s) with invalid accommodation_id', n;
    END IF;

    SELECT COUNT(*) INTO n
    FROM accommodation_images ai
    LEFT JOIN images i ON i.id = ai.image_id
    WHERE i.id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All accommodation_images have valid image_id';
    ELSE
        RAISE WARNING 'FAIL | % row(s) with invalid image_id', n;
    END IF;

    RAISE NOTICE '==== END test_accommodation_images_fk_integrity ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payment_methods_have_valid_customer
-- payment_methods.customer_id must reference a valid account
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_payment_methods_have_valid_customer ====';

    SELECT COUNT(*) INTO n
    FROM payment_methods pm
    LEFT JOIN accounts a ON a.id = pm.customer_id
    WHERE pm.customer_id IS NOT NULL
      AND a.id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All payment_methods have valid customer_id (or NULL)';
    ELSE
        RAISE WARNING 'FAIL | % payment_method(s) with invalid customer_id', n;
    END IF;

    RAISE NOTICE '==== END test_payment_methods_have_valid_customer ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payment_method_details_exclusive_and_complete
-- Each payment_method has exactly one detail: card XOR paypal
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_payment_method_details_exclusive_and_complete ====';

    -- Orphan credit_cards
    SELECT COUNT(*) INTO n
    FROM credit_cards cc
    LEFT JOIN payment_methods pm ON pm.id = cc.payment_method_id
    WHERE pm.id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All credit_cards have valid payment_method_id';
    ELSE
        RAISE WARNING 'FAIL | % orphan credit_card row(s)', n;
    END IF;

    -- Orphan paypal rows
    SELECT COUNT(*) INTO n
    FROM paypal pp
    LEFT JOIN payment_methods pm ON pm.id = pp.payment_method_id
    WHERE pm.id IS NULL;
    IF n = 0 THEN
        RAISE NOTICE 'PASS | All paypal rows have valid payment_method_id';
    ELSE
        RAISE WARNING 'FAIL | % orphan paypal row(s)', n;
    END IF;

    -- XOR check: must have exactly one of (card, paypal)
    SELECT COUNT(*) INTO n
    FROM payment_methods pm
    LEFT JOIN credit_cards cc ON cc.payment_method_id = pm.id
    LEFT JOIN paypal       pp ON pp.payment_method_id = pm.id
    WHERE (cc.payment_method_id IS NOT NULL AND pp.payment_method_id IS NOT NULL)
       OR (cc.payment_method_id IS NULL     AND pp.payment_method_id IS NULL);
    IF n = 0 THEN
        RAISE NOTICE 'PASS | Each payment_method has exactly one detail row (card XOR paypal)';
    ELSE
        RAISE WARNING 'FAIL | % payment_method(s) violate XOR exclusivity', n;
    END IF;

    RAISE NOTICE '==== END test_payment_method_details_exclusive_and_complete ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_reviews_and_review_images_integrity
-- reviews → accommodations/accounts; review_images → reviews/images
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_reviews_and_review_images_integrity ====';

    SELECT COUNT(*) INTO n
    FROM reviews r
    LEFT JOIN accommodations a ON a.id = r.accommodation_id
    WHERE a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All reviews have valid accommodation_id';
    ELSE RAISE WARNING 'FAIL | % review(s) with invalid accommodation_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM reviews r
    LEFT JOIN accounts acc ON acc.id = r.author_account_id
    WHERE acc.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All reviews have valid author_account_id';
    ELSE RAISE WARNING 'FAIL | % review(s) with invalid author_account_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM review_images ri
    LEFT JOIN reviews r ON r.id = ri.review_id
    WHERE r.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All review_images have valid review_id';
    ELSE RAISE WARNING 'FAIL | % review_image(s) with invalid review_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM review_images ri
    LEFT JOIN images i ON i.id = ri.image_id
    WHERE i.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All review_images have valid image_id';
    ELSE RAISE WARNING 'FAIL | % review_image(s) with invalid image_id', n; END IF;

    RAISE NOTICE '==== END test_reviews_and_review_images_integrity ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_messages_integrity
-- messages → accounts (sender/receiver) and conversations
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_messages_integrity ====';

    SELECT COUNT(*) INTO n
    FROM messages m
    LEFT JOIN accounts a ON a.id = m.sender_id
    WHERE a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All messages have valid sender_id';
    ELSE RAISE WARNING 'FAIL | % message(s) with invalid sender_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM messages m
    LEFT JOIN accounts a ON a.id = m.receiver_id
    WHERE a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All messages have valid receiver_id';
    ELSE RAISE WARNING 'FAIL | % message(s) with invalid receiver_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM messages m
    LEFT JOIN conversations c ON c.id = m.conversation_id
    WHERE c.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All messages have valid conversation_id';
    ELSE RAISE WARNING 'FAIL | % message(s) with invalid conversation_id', n; END IF;

    RAISE NOTICE '==== END test_messages_integrity ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payout_accounts_integrity
-- payout_accounts.host_account_id → accounts
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_payout_accounts_integrity ====';

    SELECT COUNT(*) INTO n
    FROM payout_accounts pa
    LEFT JOIN accounts a ON a.id = pa.host_account_id
    WHERE pa.host_account_id IS NOT NULL
      AND a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All payout_accounts have valid host_account_id (or NULL)';
    ELSE RAISE WARNING 'FAIL | % payout_account(s) with invalid host_account_id', n; END IF;

    RAISE NOTICE '==== END test_payout_accounts_integrity ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payouts_integrity
-- payouts → accounts, payout_accounts, bookings
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_payouts_integrity ====';

    SELECT COUNT(*) INTO n
    FROM payouts p
    LEFT JOIN accounts a ON a.id = p.host_account_id
    WHERE p.host_account_id IS NOT NULL AND a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All payouts have valid host_account_id (or NULL)';
    ELSE RAISE WARNING 'FAIL | % payout(s) with invalid host_account_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM payouts p
    LEFT JOIN payout_accounts pa ON pa.id = p.payout_account_id
    WHERE p.payout_account_id IS NOT NULL AND pa.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All payouts have valid payout_account_id (or NULL)';
    ELSE RAISE WARNING 'FAIL | % payout(s) with invalid payout_account_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM payouts p
    LEFT JOIN bookings b ON b.id = p.booking_id
    WHERE p.booking_id IS NOT NULL AND b.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All payouts have valid booking_id (or NULL)';
    ELSE RAISE WARNING 'FAIL | % payout(s) with invalid booking_id', n; END IF;

    RAISE NOTICE '==== END test_payouts_integrity ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_notifications_integrity
-- notifications.account_id → accounts
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_notifications_integrity ====';

    SELECT COUNT(*) INTO n
    FROM notifications n2
    LEFT JOIN accounts a ON a.id = n2.account_id
    WHERE n2.account_id IS NOT NULL AND a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All notifications have valid account_id (or NULL)';
    ELSE RAISE WARNING 'FAIL | % notification(s) with invalid account_id', n; END IF;

    RAISE NOTICE '==== END test_notifications_integrity ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payments_integrity
-- payments → accounts and payment_methods
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_payments_integrity ====';

    SELECT COUNT(*) INTO n
    FROM payments p
    LEFT JOIN accounts a ON a.id = p.customer_id
    WHERE p.customer_id IS NOT NULL AND a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All payments have valid customer_id (or NULL)';
    ELSE RAISE WARNING 'FAIL | % payment(s) with invalid customer_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM payments p
    LEFT JOIN payment_methods pm ON pm.id = p.payment_method_id
    WHERE p.payment_method_id IS NOT NULL AND pm.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All payments have valid payment_method_id';
    ELSE RAISE WARNING 'FAIL | % payment(s) with invalid payment_method_id', n; END IF;

    RAISE NOTICE '==== END test_payments_integrity ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_bookings_integrity
-- bookings → accounts (guest), accommodations, payments
-- ------------------------------------------------------------
DO $$
DECLARE
    n INT;
BEGIN
    RAISE NOTICE '==== test_bookings_integrity ====';

    SELECT COUNT(*) INTO n
    FROM bookings b
    LEFT JOIN accounts a ON a.id = b.guest_account_id
    WHERE a.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All bookings have valid guest_account_id';
    ELSE RAISE WARNING 'FAIL | % booking(s) with invalid guest_account_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM bookings b
    LEFT JOIN accommodations ac ON ac.id = b.accommodation_id
    WHERE ac.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All bookings have valid accommodation_id';
    ELSE RAISE WARNING 'FAIL | % booking(s) with invalid accommodation_id', n; END IF;

    SELECT COUNT(*) INTO n
    FROM bookings b
    LEFT JOIN payments p ON p.id = b.payment_id
    WHERE b.payment_id IS NOT NULL AND p.id IS NULL;
    IF n = 0 THEN RAISE NOTICE 'PASS | All bookings have valid payment_id (or NULL)';
    ELSE RAISE WARNING 'FAIL | % booking(s) with invalid payment_id', n; END IF;

    RAISE NOTICE '==== END test_bookings_integrity ====';
END $$;


-- ============================================================
-- === SECTION 2: FAULTY DATA INSERTION TESTS ===
-- Each block uses SAVEPOINT so one sub-test failure doesn't
-- abort the outer transaction — always rolls back fully.
-- ============================================================


-- ------------------------------------------------------------
-- TEST: test_accounts (duplicate email must fail)
-- ------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE '==== test_accounts (faulty insertion) ====';

    SAVEPOINT sp_accounts;
    INSERT INTO accounts (email) VALUES ('a@test.com');

    BEGIN
        INSERT INTO accounts (email) VALUES ('a@test.com'); -- must fail
        RAISE WARNING 'FAIL | Duplicate email was accepted (expected constraint violation)';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Duplicate email correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_accounts;
    RAISE NOTICE '==== END test_accounts ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_credentials (orphan credential must fail)
-- ------------------------------------------------------------
DO $$
DECLARE
    acc_id INT;
BEGIN
    RAISE NOTICE '==== test_credentials (faulty insertion) ====';

    SAVEPOINT sp_cred;
    INSERT INTO accounts (email) VALUES ('cred@test.com') RETURNING id INTO acc_id;
    INSERT INTO credentials (account_id, password_hash) VALUES (acc_id, 'hash');
    RAISE NOTICE 'PASS | Valid credential inserted';

    BEGIN
        INSERT INTO credentials (account_id, password_hash) VALUES (9999, 'fail');
        RAISE WARNING 'FAIL | Orphan credential was accepted (expected FK violation)';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Orphan credential correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_cred;
    RAISE NOTICE '==== END test_credentials (faulty insertion) ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_addresses (missing NOT NULL column must fail)
-- ------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE '==== test_addresses (faulty insertion) ====';

    SAVEPOINT sp_addr;
    INSERT INTO addresses (line1, city, country) VALUES ('L1','Berlin','DE');
    RAISE NOTICE 'PASS | Valid address inserted';

    BEGIN
        INSERT INTO addresses (city, country) VALUES ('Berlin','DE'); -- missing line1
        RAISE WARNING 'FAIL | Address without line1 was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Address without line1 correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_addr;
    RAISE NOTICE '==== END test_addresses ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_amenities (duplicate name must fail)
-- ------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE '==== test_amenities (faulty insertion) ====';

    SAVEPOINT sp_amen;
    INSERT INTO amenities (name) VALUES ('WiFi');
    RAISE NOTICE 'PASS | First amenity inserted';

    BEGIN
        INSERT INTO amenities (name) VALUES ('WiFi'); -- duplicate
        RAISE WARNING 'FAIL | Duplicate amenity name was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Duplicate amenity name correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_amen;
    RAISE NOTICE '==== END test_amenities ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_accommodations (negative price must fail)
-- ------------------------------------------------------------
DO $$
DECLARE
    host_id INT;
BEGIN
    RAISE NOTICE '==== test_accommodations (faulty insertion) ====';

    SAVEPOINT sp_acc;
    INSERT INTO accounts (email, role) VALUES ('host@test.com','host') RETURNING id INTO host_id;
    INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host_id,'Test',1000);
    RAISE NOTICE 'PASS | Valid accommodation inserted';

    BEGIN
        INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host_id,'Bad',-1);
        RAISE WARNING 'FAIL | Negative price_cents was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Negative price_cents correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_acc;
    RAISE NOTICE '==== END test_accommodations ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_accommodation_amenities (duplicate PK must fail)
-- ------------------------------------------------------------
DO $$
DECLARE
    host_id   INT;
    acc_id    INT;
    amenity_id INT;
BEGIN
    RAISE NOTICE '==== test_accommodation_amenities (faulty insertion) ====';

    SAVEPOINT sp_acc_amen;
    INSERT INTO accounts (email) VALUES ('h2@test.com') RETURNING id INTO host_id;
    INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host_id,'A',100);
    SELECT id INTO acc_id FROM accommodations WHERE title = 'A';
    INSERT INTO amenities (name) VALUES ('Kitchen') RETURNING id INTO amenity_id;
    INSERT INTO accommodation_amenities VALUES (acc_id, amenity_id);
    RAISE NOTICE 'PASS | First accommodation_amenity inserted';

    BEGIN
        INSERT INTO accommodation_amenities VALUES (acc_id, amenity_id); -- duplicate
        RAISE WARNING 'FAIL | Duplicate accommodation_amenity was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Duplicate accommodation_amenity correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_acc_amen;
    RAISE NOTICE '==== END test_accommodation_amenities ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_images (duplicate storage_key must fail)
-- ------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE '==== test_images (faulty insertion) ====';

    SAVEPOINT sp_img;
    INSERT INTO images (mime, storage_key) VALUES ('img','key1');
    RAISE NOTICE 'PASS | First image inserted';

    BEGIN
        INSERT INTO images (mime, storage_key) VALUES ('img','key1'); -- duplicate
        RAISE WARNING 'FAIL | Duplicate storage_key was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Duplicate storage_key correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_img;
    RAISE NOTICE '==== END test_images ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_accommodation_images (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    host_id INT;
    acc_id  INT;
    img_id  INT;
BEGIN
    RAISE NOTICE '==== test_accommodation_images ====';

    SAVEPOINT sp_acc_img;
    INSERT INTO accounts (email) VALUES ('h3@test.com') RETURNING id INTO host_id;
    INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host_id,'B',100);
    SELECT id INTO acc_id FROM accommodations WHERE title = 'B';
    INSERT INTO images (mime, storage_key) VALUES ('img','key2') RETURNING id INTO img_id;
    INSERT INTO accommodation_images VALUES (acc_id, img_id, 1, TRUE, 'c', 'room');
    RAISE NOTICE 'PASS | accommodation_image inserted';

    ROLLBACK TO SAVEPOINT sp_acc_img;
    RAISE NOTICE '==== END test_accommodation_images ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_accommodation_calendar (duplicate date must fail)
-- ------------------------------------------------------------
DO $$
DECLARE
    host_id INT;
    acc_id  INT;
BEGIN
    RAISE NOTICE '==== test_accommodation_calendar (faulty insertion) ====';

    SAVEPOINT sp_cal;
    INSERT INTO accounts (email) VALUES ('h4@test.com') RETURNING id INTO host_id;
    INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host_id,'C',100);
    SELECT id INTO acc_id FROM accommodations WHERE title = 'C';
    INSERT INTO accommodation_calendar VALUES (acc_id, CURRENT_DATE, FALSE, 0, 1);
    RAISE NOTICE 'PASS | First calendar entry inserted';

    BEGIN
        INSERT INTO accommodation_calendar VALUES (acc_id, CURRENT_DATE, FALSE, 0, 1); -- duplicate
        RAISE WARNING 'FAIL | Duplicate calendar entry was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Duplicate calendar entry correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_cal;
    RAISE NOTICE '==== END test_accommodation_calendar ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payment_methods (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    acc_id INT;
BEGIN
    RAISE NOTICE '==== test_payment_methods ====';

    SAVEPOINT sp_pm;
    INSERT INTO accounts (email) VALUES ('pay@test.com') RETURNING id INTO acc_id;
    INSERT INTO payment_methods (customer_id, type) VALUES (acc_id, 'card');
    RAISE NOTICE 'PASS | payment_method inserted';

    ROLLBACK TO SAVEPOINT sp_pm;
    RAISE NOTICE '==== END test_payment_methods ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payments (negative amount must fail)
-- ------------------------------------------------------------
DO $$
DECLARE
    acc_id INT;
    pm_id  INT;
BEGIN
    RAISE NOTICE '==== test_payments (faulty insertion) ====';

    SAVEPOINT sp_pay;
    INSERT INTO accounts (email) VALUES ('p2@test.com') RETURNING id INTO acc_id;
    INSERT INTO payment_methods (customer_id, type) VALUES (acc_id, 'card') RETURNING id INTO pm_id;
    INSERT INTO payments (customer_id, amount_cents, status, payment_method_id)
        VALUES (acc_id, 100, 'open', pm_id);
    RAISE NOTICE 'PASS | Valid payment inserted';

    BEGIN
        INSERT INTO payments (customer_id, amount_cents, status, payment_method_id)
            VALUES (acc_id, -1, 'open', pm_id);
        RAISE WARNING 'FAIL | Negative amount_cents was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Negative amount_cents correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_pay;
    RAISE NOTICE '==== END test_payments ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_bookings (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    guest  INT;
    host   INT;
    acc_id INT;
BEGIN
    RAISE NOTICE '==== test_bookings ====';

    SAVEPOINT sp_book;
    INSERT INTO accounts (email) VALUES ('g@test.com')  RETURNING id INTO guest;
    INSERT INTO accounts (email) VALUES ('h5@test.com') RETURNING id INTO host;
    INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host,'D',100);
    SELECT id INTO acc_id FROM accommodations WHERE title = 'D';
    INSERT INTO bookings (guest_account_id, accommodation_id, start_date, end_date)
        VALUES (guest, acc_id, NOW(), NOW());
    RAISE NOTICE 'PASS | Booking inserted';

    ROLLBACK TO SAVEPOINT sp_book;
    RAISE NOTICE '==== END test_bookings ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_reviews (rating > 5 must fail)
-- ------------------------------------------------------------
DO $$
DECLARE
    user_id INT;
    host    INT;
    acc_id  INT;
BEGIN
    RAISE NOTICE '==== test_reviews (faulty insertion) ====';

    SAVEPOINT sp_rev;
    INSERT INTO accounts (email) VALUES ('rev@test.com') RETURNING id INTO user_id;
    INSERT INTO accounts (email) VALUES ('h6@test.com')  RETURNING id INTO host;
    INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host,'E',100);
    SELECT id INTO acc_id FROM accommodations WHERE title = 'E';
    INSERT INTO reviews (accommodation_id, author_account_id, rating) VALUES (acc_id, user_id, 5);
    RAISE NOTICE 'PASS | Valid review (rating=5) inserted';

    BEGIN
        INSERT INTO reviews (accommodation_id, author_account_id, rating) VALUES (acc_id, user_id, 6);
        RAISE WARNING 'FAIL | Rating > 5 was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | Rating > 5 correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_rev;
    RAISE NOTICE '==== END test_reviews ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_review_images (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    img_id    INT;
    user_id   INT;
    host      INT;
    acc_id    INT;
    review_id INT;
BEGIN
    RAISE NOTICE '==== test_review_images ====';

    SAVEPOINT sp_ri;
    INSERT INTO images (mime, storage_key) VALUES ('img','key3') RETURNING id INTO img_id;
    INSERT INTO accounts (email) VALUES ('r2@test.com') RETURNING id INTO user_id;
    INSERT INTO accounts (email) VALUES ('h7@test.com') RETURNING id INTO host;
    INSERT INTO accommodations (host_account_id, title, price_cents) VALUES (host,'F',100);
    SELECT id INTO acc_id FROM accommodations WHERE title = 'F';
    INSERT INTO reviews (accommodation_id, author_account_id, rating)
        VALUES (acc_id, user_id, 4) RETURNING id INTO review_id;
    INSERT INTO review_images VALUES (review_id, img_id);
    RAISE NOTICE 'PASS | review_image inserted';

    ROLLBACK TO SAVEPOINT sp_ri;
    RAISE NOTICE '==== END test_review_images ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_conversations (default insert)
-- ------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE '==== test_conversations ====';

    SAVEPOINT sp_conv;
    INSERT INTO conversations DEFAULT VALUES;
    RAISE NOTICE 'PASS | Conversation inserted with DEFAULT VALUES';

    ROLLBACK TO SAVEPOINT sp_conv;
    RAISE NOTICE '==== END test_conversations ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_messages (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    sender   INT;
    receiver INT;
    conv     INT;
BEGIN
    RAISE NOTICE '==== test_messages ====';

    SAVEPOINT sp_msg;
    INSERT INTO accounts (email) VALUES ('s@test.com') RETURNING id INTO sender;
    INSERT INTO accounts (email) VALUES ('r@test.com') RETURNING id INTO receiver;
    INSERT INTO conversations DEFAULT VALUES RETURNING id INTO conv;
    INSERT INTO messages (sender_id, receiver_id, conversation_id, body)
        VALUES (sender, receiver, conv, 'hi');
    RAISE NOTICE 'PASS | Message inserted';

    ROLLBACK TO SAVEPOINT sp_msg;
    RAISE NOTICE '==== END test_messages ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_credit_cards (exp_month > 12 must fail)
-- ------------------------------------------------------------
DO $$
DECLARE
    acc INT;
    pm  INT;
BEGIN
    RAISE NOTICE '==== test_credit_cards (faulty insertion) ====';

    SAVEPOINT sp_cc;
    INSERT INTO accounts (email) VALUES ('cc@test.com') RETURNING id INTO acc;
    INSERT INTO payment_methods (customer_id, type) VALUES (acc,'card') RETURNING id INTO pm;
    INSERT INTO credit_cards (payment_method_id, exp_month) VALUES (pm, 12);
    RAISE NOTICE 'PASS | Valid credit card (month=12) inserted';

    BEGIN
        INSERT INTO credit_cards (payment_method_id, exp_month) VALUES (pm, 13);
        RAISE WARNING 'FAIL | exp_month=13 was accepted';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'PASS | exp_month=13 correctly rejected: %', SQLERRM;
    END;

    ROLLBACK TO SAVEPOINT sp_cc;
    RAISE NOTICE '==== END test_credit_cards ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_paypal (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    acc INT;
    pm  INT;
BEGIN
    RAISE NOTICE '==== test_paypal ====';

    SAVEPOINT sp_pp;
    INSERT INTO accounts (email) VALUES ('pp@test.com') RETURNING id INTO acc;
    INSERT INTO payment_methods (customer_id, type) VALUES (acc,'paypal') RETURNING id INTO pm;
    INSERT INTO paypal (payment_method_id, paypal_user_id, email) VALUES (pm,'u1','e1@test.com');
    RAISE NOTICE 'PASS | PayPal row inserted';

    ROLLBACK TO SAVEPOINT sp_pp;
    RAISE NOTICE '==== END test_paypal ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payout_accounts (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    host INT;
BEGIN
    RAISE NOTICE '==== test_payout_accounts ====';

    SAVEPOINT sp_pa;
    INSERT INTO accounts (email) VALUES ('host8@test.com') RETURNING id INTO host;
    INSERT INTO payout_accounts (host_account_id, type) VALUES (host,'card');
    RAISE NOTICE 'PASS | payout_account inserted';

    ROLLBACK TO SAVEPOINT sp_pa;
    RAISE NOTICE '==== END test_payout_accounts ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_payouts (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    host       INT;
    payout_acc INT;
BEGIN
    RAISE NOTICE '==== test_payouts ====';

    SAVEPOINT sp_pout;
    INSERT INTO accounts (email) VALUES ('host9@test.com') RETURNING id INTO host;
    INSERT INTO payout_accounts (host_account_id, type) VALUES (host,'card') RETURNING id INTO payout_acc;
    INSERT INTO payouts (host_account_id, payout_account_id, amount_cents) VALUES (host, payout_acc, 1000);
    RAISE NOTICE 'PASS | payout inserted';

    ROLLBACK TO SAVEPOINT sp_pout;
    RAISE NOTICE '==== END test_payouts ====';
END $$;


-- ------------------------------------------------------------
-- TEST: test_notifications (valid insert only)
-- ------------------------------------------------------------
DO $$
DECLARE
    acc INT;
BEGIN
    RAISE NOTICE '==== test_notifications ====';

    SAVEPOINT sp_notif;
    INSERT INTO accounts (email) VALUES ('notif@test.com') RETURNING id INTO acc;
    INSERT INTO notifications (account_id, payload) VALUES (acc,'{"type":"test"}');
    RAISE NOTICE 'PASS | Notification inserted';

    ROLLBACK TO SAVEPOINT sp_notif;
    RAISE NOTICE '==== END test_notifications ====';
END $$;

-- ============================================================
-- END OF TEST SUITE
-- All blocks used SAVEPOINT + ROLLBACK TO SAVEPOINT internally
-- No persistent data was written to the database
-- ============================================================