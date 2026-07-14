import pytest
from datetime import date

from src.db.connection import db_connection

# 0. Create Connection for all tests and rollback later
@pytest.fixture(scope="module")
def conn():
    connection = db_connection()
    connection.autocommit = False
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


# 0.1. Create state fixture to store values in global scope
@pytest.fixture(scope="module")
def state():
    return {}


# 1. Create host account
# Related table:
# accounts(id, email, first_name, last_name, role, created_at)
# Test steps:
# - Insert one account with role = 'host'.
# - Store the returned host id.
# - Assert that the id is not None.
# - Select the account again by id.
# - Assert that email and role match the inserted values.
def test_01_create_host_account(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO accounts (email, first_name, last_name, role)
        VALUES ('host@test.com', 'John', 'Host', 'host')
        RETURNING id
    """)
    host_id = cur.fetchone()[0]
    state["host_id"] = host_id

    assert host_id is not None

    cur.execute("""
        SELECT email, role
        FROM accounts
        WHERE id = %s
    """, (host_id,))
    email, role = cur.fetchone()

    assert email == "host@test.com"
    assert role == "host"


# 2. Create guest/customer account
# Related table:
# accounts(id, email, first_name, last_name, role, created_at)
# Test steps:
# - Insert one account with role = 'guest'.
# - Store the returned guest id.
# - Assert that the id is not None.
# - Select the account again by id.
# - Assert that email and role match the inserted values.
def test_02_create_guest_account(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO accounts (email, first_name, last_name, role)
        VALUES ('guest@test.com', 'Jane', 'Guest', 'guest')
        RETURNING id
    """)
    guest_id = cur.fetchone()[0]
    state["guest_id"] = guest_id

    assert guest_id is not None

    cur.execute("""
        SELECT email, role
        FROM accounts
        WHERE id = %s
    """, (guest_id,))
    email, role = cur.fetchone()

    assert email == "guest@test.com"
    assert role == "guest"


# 3. Create accommodation address
# Related table:
# addresses(id, line1, line2, city, postal_code, country)
# Test steps:
# - Insert one address.
# - Store the returned address id.
# - Assert that the id is not None.
# - Select the address again by id.
# - Assert that line1, city, postal_code, and country match the inserted values.
def test_03_create_accommodation_address(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO addresses (line1, line2, city, postal_code, country)
        VALUES ('Main Street 1', 'Apartment 2', 'Munich', '80331', 'Germany')
        RETURNING id
    """)
    address_id = cur.fetchone()[0]
    state["address_id"] = address_id

    assert address_id is not None

    cur.execute("""
        SELECT line1, city, postal_code, country
        FROM addresses
        WHERE id = %s
    """, (address_id,))
    line1, city, postal_code, country = cur.fetchone()

    assert line1 == "Main Street 1"
    assert city == "Munich"
    assert postal_code == "80331"
    assert country == "Germany"


# 4. Create accommodation owned by host
# Related tables:
# accommodations(id, host_account_id, title, address_id, price_cents, is_active, created_at)
# accounts(id) referenced by accommodations.host_account_id
# addresses(id) referenced by accommodations.address_id
# Test steps:
# - Insert one accommodation using the host id and address id.
# - Store the returned accommodation id.
# - Assert that the id is not None.
# - Select the accommodation again by id.
# - Assert that host_account_id equals the host id.
# - Assert that address_id equals the address id.
# - Assert that title, price_cents, and is_active match the expected values.
def test_04_create_accommodation_owned_by_host(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO accommodations (host_account_id, title, address_id, price_cents, is_active)
        VALUES (%s, 'Business Logic Apartment', %s, 12000, TRUE)
        RETURNING id
    """, (state["host_id"], state["address_id"]))
    accommodation_id = cur.fetchone()[0]
    state["accommodation_id"] = accommodation_id
    state["base_price_cents"] = 12000

    assert accommodation_id is not None

    cur.execute("""
        SELECT host_account_id, title, address_id, price_cents, is_active
        FROM accommodations
        WHERE id = %s
    """, (accommodation_id,))
    host_account_id, title, address_id, price_cents, is_active = cur.fetchone()

    assert host_account_id == state["host_id"]
    assert address_id == state["address_id"]
    assert title == "Business Logic Apartment"
    assert price_cents == 12000
    assert is_active is True


# 5. Add amenities to accommodation
# Related tables:
# amenities(id, name, category)
# accommodation_amenities(accommodation_id, amenity_id)
# accommodations(id) referenced by accommodation_amenities.accommodation_id
# amenities(id) referenced by accommodation_amenities.amenity_id
# Test steps:
# - Insert one or more amenities.
# - Store the returned amenity ids.
# - Insert rows into accommodation_amenities using the accommodation id and amenity ids.
# - Select amenities through a JOIN from accommodation_amenities to amenities.
# - Assert that the accommodation has the expected amenities.
# - Assert that the number of linked amenities matches the inserted number.
def test_05_add_amenities_to_accommodation(conn, state):
    cur = conn.cursor()

    expected_amenities = [("WiFi", "internet"), ("Kitchen", "facility")]

    amenity_ids = []
    for name, category in expected_amenities:
        cur.execute("""
            INSERT INTO amenities (name, category)
            VALUES (%s, %s)
            RETURNING id
        """, (name, category))
        amenity_ids.append(cur.fetchone()[0])

    for amenity_id in amenity_ids:
        cur.execute("""
            INSERT INTO accommodation_amenities (accommodation_id, amenity_id)
            VALUES (%s, %s)
        """, (state["accommodation_id"], amenity_id))

    state["amenity_ids"] = amenity_ids

    cur.execute("""
        SELECT a.name, a.category
        FROM accommodation_amenities aa
        JOIN amenities a ON a.id = aa.amenity_id
        WHERE aa.accommodation_id = %s
        ORDER BY a.name
    """, (state["accommodation_id"],))
    rows = cur.fetchall()

    assert rows == [("Kitchen", "facility"), ("WiFi", "internet")]
    assert len(rows) == len(expected_amenities)


# 6. Add accommodation images
# Related tables:
# images(id, mime, storage_key, created_at)
# accommodation_images(accommodation_id, image_id, sort_order, is_cover, caption, room_tag)
# accommodations(id) referenced by accommodation_images.accommodation_id
# images(id) referenced by accommodation_images.image_id
# Test steps:
# - Insert one or more image records.
# - Store the returned image ids.
# - Insert rows into accommodation_images using the accommodation id and image ids.
# - Mark exactly one image as cover.
# - Select images through a JOIN from accommodation_images to images.
# - Assert that the expected storage_key values are returned.
# - Assert that exactly one image is marked as is_cover = TRUE.
def test_06_add_accommodation_images(conn, state):
    cur = conn.cursor()

    images = [
        ("image/jpeg", "business_logic_apartment_cover.jpg", 1, True, "Cover image", "living_room"),
        ("image/jpeg", "business_logic_apartment_bedroom.jpg", 2, False, "Bedroom image", "bedroom"),
    ]

    image_ids = []
    for mime, storage_key, sort_order, is_cover, caption, room_tag in images:
        cur.execute("""
            INSERT INTO images (mime, storage_key)
            VALUES (%s, %s)
            RETURNING id
        """, (mime, storage_key))
        image_id = cur.fetchone()[0]
        image_ids.append(image_id)

        cur.execute("""
            INSERT INTO accommodation_images (
                accommodation_id, image_id, sort_order, is_cover, caption, room_tag
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            state["accommodation_id"],
            image_id,
            sort_order,
            is_cover,
            caption,
            room_tag,
        ))

    state["image_ids"] = image_ids

    cur.execute("""
        SELECT i.storage_key, ai.is_cover, ai.sort_order
        FROM accommodation_images ai
        JOIN images i ON i.id = ai.image_id
        WHERE ai.accommodation_id = %s
        ORDER BY ai.sort_order
    """, (state["accommodation_id"],))
    rows = cur.fetchall()

    assert [row[0] for row in rows] == [
        "business_logic_apartment_cover.jpg",
        "business_logic_apartment_bedroom.jpg",
    ]
    assert sum(row[1] for row in rows) == 1
    assert [row[2] for row in rows] == [1, 2]


# 7. Add calendar availability for accommodation
# Related table:
# accommodation_calendar(accommodation_id, day, is_blocked, price_addition_cents, min_nights)
# accommodations(id) referenced by accommodation_calendar.accommodation_id
# Test steps:
# - Insert several calendar days for the accommodation.
# - Use is_blocked = FALSE for available days.
# - Store the intended booking date range.
# - Select calendar rows for the selected date range.
# - Assert that all expected days exist.
# - Assert that all selected days have is_blocked = FALSE.
# - Assert that min_nights allows the intended stay duration.
def test_07_add_calendar_availability_for_accommodation(conn, state):
    cur = conn.cursor()

    state["booking_start_date"] = date(2026, 8, 10)
    state["booking_end_date"] = date(2026, 8, 13)
    state["booking_nights"] = 3

    calendar_days = [
        (date(2026, 8, 10), False, 0, 2),
        (date(2026, 8, 11), False, 1000, 2),
        (date(2026, 8, 12), False, 0, 2),
    ]

    for day, is_blocked, price_addition_cents, min_nights in calendar_days:
        cur.execute("""
            INSERT INTO accommodation_calendar (
                accommodation_id, day, is_blocked, price_addition_cents, min_nights
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            state["accommodation_id"],
            day,
            is_blocked,
            price_addition_cents,
            min_nights,
        ))

    cur.execute("""
        SELECT day, is_blocked, price_addition_cents, min_nights
        FROM accommodation_calendar
        WHERE accommodation_id = %s
          AND day >= %s
          AND day < %s
        ORDER BY day
    """, (
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))
    rows = cur.fetchall()

    assert len(rows) == state["booking_nights"]
    assert all(row[1] is False for row in rows)
    assert all(row[3] <= state["booking_nights"] for row in rows)


# 8. Customer searches active accommodations
# Related table:
# accommodations(id, host_account_id, title, address_id, price_cents, is_active, created_at)
# Test steps:
# - Query accommodations where is_active = TRUE.
# - Optionally join addresses to simulate city/country search.
# - Assert that the created accommodation appears in the result.
# - Assert that the returned accommodation has the expected title and price.
# - Optionally insert an inactive accommodation and assert that it does not appear.
def test_08_customer_searches_active_accommodations(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO accommodations (host_account_id, title, address_id, price_cents, is_active)
        VALUES (%s, 'Inactive Test Apartment', %s, 9000, FALSE)
        RETURNING id
    """, (state["host_id"], state["address_id"]))
    inactive_accommodation_id = cur.fetchone()[0]

    cur.execute("""
        SELECT id, title, price_cents
        FROM accommodations
        WHERE is_active = TRUE
        ORDER BY id
    """)
    rows = cur.fetchall()
    active_ids = [row[0] for row in rows]

    assert state["accommodation_id"] in active_ids
    assert inactive_accommodation_id not in active_ids

    selected = [row for row in rows if row[0] == state["accommodation_id"]][0]
    assert selected[1] == "Business Logic Apartment"
    assert selected[2] == state["base_price_cents"]


# 9. Customer checks selected accommodation price
# Related table:
# accommodations(id, price_cents)
# Test steps:
# - Select price_cents for the selected accommodation.
# - Assert that price_cents equals the inserted base price.
# - Optionally calculate expected total price from number of nights and calendar additions.
# - Assert that the calculated total price matches the expected amount.
def test_09_customer_checks_selected_accommodation_price(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT price_cents
        FROM accommodations
        WHERE id = %s
    """, (state["accommodation_id"],))
    base_price_cents = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(price_addition_cents), 0)
        FROM accommodation_calendar
        WHERE accommodation_id = %s
          AND day >= %s
          AND day < %s
    """, (
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))
    price_additions_cents = cur.fetchone()[0]

    expected_total_cents = (base_price_cents * state["booking_nights"]) + price_additions_cents
    state["expected_total_cents"] = expected_total_cents

    assert base_price_cents == state["base_price_cents"]
    assert expected_total_cents == 37000


# 10. Customer checks selected accommodation images
# Related tables:
# accommodation_images(accommodation_id, image_id, sort_order, is_cover, caption, room_tag)
# images(id, mime, storage_key, created_at)
# Test steps:
# - Select all images linked to the selected accommodation.
# - Join accommodation_images with images.
# - Assert that at least one image is returned.
# - Assert that the expected storage_key values are present.
# - Assert that exactly one image is marked as cover.
# - Assert that image ordering can be retrieved through sort_order.
def test_10_customer_checks_selected_accommodation_images(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT i.storage_key, ai.is_cover, ai.sort_order
        FROM accommodation_images ai
        JOIN images i ON i.id = ai.image_id
        WHERE ai.accommodation_id = %s
        ORDER BY ai.sort_order
    """, (state["accommodation_id"],))
    rows = cur.fetchall()

    assert len(rows) > 0
    assert [row[0] for row in rows] == [
        "business_logic_apartment_cover.jpg",
        "business_logic_apartment_bedroom.jpg",
    ]
    assert sum(row[1] for row in rows) == 1
    assert [row[2] for row in rows] == [1, 2]


# 11. Customer checks available calendar dates
# Related table:
# accommodation_calendar(accommodation_id, day, is_blocked, price_addition_cents, min_nights)
# Test steps:
# - Select calendar rows for the selected accommodation.
# - Filter for days where is_blocked = FALSE.
# - Assert that available dates are returned.
# - Assert that the intended booking dates are included in the available dates.
# - Assert that price_addition_cents and min_nights can be read for those dates.
def test_11_customer_checks_available_calendar_dates(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT day, price_addition_cents, min_nights
        FROM accommodation_calendar
        WHERE accommodation_id = %s
          AND is_blocked = FALSE
        ORDER BY day
    """, (state["accommodation_id"],))
    rows = cur.fetchall()

    available_dates = [row[0] for row in rows]

    assert len(rows) > 0
    assert state["booking_start_date"] in available_dates
    assert date(2026, 8, 11) in available_dates
    assert date(2026, 8, 12) in available_dates
    assert all(row[1] is not None for row in rows)
    assert all(row[2] is not None for row in rows)


# 12. Customer selects available date range
# Related table:
# accommodation_calendar(accommodation_id, day, is_blocked, price_addition_cents, min_nights)
# Test steps:
# - Define a start date and end date from the available calendar rows.
# - Select all calendar rows between start date and end date.
# - Assert that the number of selected rows matches the intended number of nights.
# - Assert that the selected range belongs to the correct accommodation.
# - Assert that the selected stay length satisfies min_nights.
def test_12_customer_selects_available_date_range(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT accommodation_id, day, is_blocked, min_nights
        FROM accommodation_calendar
        WHERE accommodation_id = %s
          AND day >= %s
          AND day < %s
        ORDER BY day
    """, (
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))
    rows = cur.fetchall()

    assert len(rows) == state["booking_nights"]
    assert all(row[0] == state["accommodation_id"] for row in rows)
    assert all(row[2] is False for row in rows)
    assert all(row[3] <= state["booking_nights"] for row in rows)


# 13. System verifies selected dates are not blocked
# Related table:
# accommodation_calendar(accommodation_id, day, is_blocked, price_addition_cents, min_nights)
# Test steps:
# - Query the selected date range for blocked dates.
# - Count rows where is_blocked = TRUE.
# - Assert that the blocked-date count is 0.
# - Assert that all selected dates are bookable before creating the booking.
def test_13_system_verifies_selected_dates_are_not_blocked(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM accommodation_calendar
        WHERE accommodation_id = %s
          AND day >= %s
          AND day < %s
          AND is_blocked = TRUE
    """, (
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))
    blocked_count = cur.fetchone()[0]

    assert blocked_count == 0


# 14. System creates booking with status pending
# Related table:
# bookings(id, guest_account_id, accommodation_id, start_date, end_date, payment_id, status, created_at)
# accounts(id) referenced by bookings.guest_account_id
# accommodations(id) referenced by bookings.accommodation_id
# Test steps:
# - Insert a booking using guest_account_id, accommodation_id, start_date, and end_date.
# - Set status = 'pending' explicitly, or rely on the default value.
# - Leave payment_id NULL initially.
# - Store the returned booking id.
# - Assert that the booking id is not None.
# - Select the booking again by id.
# - Assert that guest_account_id equals the guest id.
# - Assert that accommodation_id equals the accommodation id.
# - Assert that payment_id is NULL.
# - Assert that status is 'pending'.
def test_14_system_creates_booking_with_status_pending(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bookings (
            guest_account_id, accommodation_id, start_date, end_date, payment_id, status
        )
        VALUES (%s, %s, %s, %s, NULL, 'pending')
        RETURNING id
    """, (
        state["guest_id"],
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))
    booking_id = cur.fetchone()[0]
    state["booking_id"] = booking_id

    assert booking_id is not None

    cur.execute("""
        SELECT guest_account_id, accommodation_id, payment_id, status
        FROM bookings
        WHERE id = %s
    """, (booking_id,))
    guest_account_id, accommodation_id, payment_id, status = cur.fetchone()

    assert guest_account_id == state["guest_id"]
    assert accommodation_id == state["accommodation_id"]
    assert payment_id is None
    assert status == "pending"


# 15. System checks booking status is pending
# Related table:
# bookings(id, status)
# Test steps:
# - Select status from bookings using the booking id.
# - Assert that the status equals 'pending'.
# - Optionally assert that the booking has no linked payment yet.
def test_15_system_checks_booking_status_is_pending(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT status, payment_id
        FROM bookings
        WHERE id = %s
    """, (state["booking_id"],))
    status, payment_id = cur.fetchone()

    assert status == "pending"
    assert payment_id is None


# 16. Customer creates/selects payment method
# Related table:
# payment_methods(id, customer_id, type, created_at)
# accounts(id) referenced by payment_methods.customer_id
# Test steps:
# - Insert a payment method for the guest account.
# - Use type = 'card' or type = 'paypal'.
# - Store the returned payment_method id.
# - Assert that the payment_method id is not None.
# - Select the payment method again by id.
# - Assert that customer_id equals the guest id.
# - Assert that type matches the selected payment method type.
def test_16_customer_creates_selects_payment_method(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payment_methods (customer_id, type)
        VALUES (%s, 'card')
        RETURNING id
    """, (state["guest_id"],))
    payment_method_id = cur.fetchone()[0]
    state["payment_method_id"] = payment_method_id

    assert payment_method_id is not None

    cur.execute("""
        SELECT customer_id, type
        FROM payment_methods
        WHERE id = %s
    """, (payment_method_id,))
    customer_id, payment_type = cur.fetchone()

    assert customer_id == state["guest_id"]
    assert payment_type == "card"


# 17. Add payment method details, e.g. credit_cards or paypal
# Related tables:
# credit_cards(id, payment_method_id, brand, last4, exp_month, exp_year)
# paypal(id, payment_method_id, paypal_user_id, email)
# payment_methods(id) referenced by credit_cards.payment_method_id
# payment_methods(id) referenced by paypal.payment_method_id
# Test steps:
# - If payment method type is 'card', insert a row into credit_cards.
# - If payment method type is 'paypal', insert a row into paypal.
# - Use the previously created payment_method id.
# - Select the detail row again by payment_method_id.
# - Assert that the detail row exists.
# - Assert that payment_method_id matches the payment method.
# - For card: assert brand, last4, exp_month, and exp_year match.
# - For paypal: assert paypal_user_id and email match.
def test_17_add_payment_method_details(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO credit_cards (payment_method_id, brand, last4, exp_month, exp_year)
        VALUES (%s, 'Visa', '4242', 12, 2030)
        RETURNING id
    """, (state["payment_method_id"],))
    credit_card_id = cur.fetchone()[0]
    state["credit_card_id"] = credit_card_id

    assert credit_card_id is not None

    cur.execute("""
        SELECT payment_method_id, brand, last4, exp_month, exp_year
        FROM credit_cards
        WHERE id = %s
    """, (credit_card_id,))
    payment_method_id, brand, last4, exp_month, exp_year = cur.fetchone()

    assert payment_method_id == state["payment_method_id"]
    assert brand == "Visa"
    assert last4 == "4242"
    assert exp_month == 12
    assert exp_year == 2030


# 18. System creates payment with status open
# Related table:
# payments(id, customer_id, amount_cents, status, payment_method_id)
# accounts(id) referenced by payments.customer_id
# payment_methods(id) referenced by payments.payment_method_id
# Test steps:
# - Calculate the expected payment amount from accommodation price and selected nights.
# - Insert a payment using customer_id, amount_cents, status = 'open', and payment_method_id.
# - Store the returned payment id.
# - Assert that the payment id is not None.
# - Select the payment again by id.
# - Assert that customer_id equals the guest id.
# - Assert that payment_method_id equals the selected payment method id.
# - Assert that amount_cents equals the expected amount.
# - Assert that status is 'open'.
def test_18_system_creates_payment_with_status_open(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payments (customer_id, amount_cents, status, payment_method_id)
        VALUES (%s, %s, 'open', %s)
        RETURNING id
    """, (
        state["guest_id"],
        state["expected_total_cents"],
        state["payment_method_id"],
    ))
    payment_id = cur.fetchone()[0]
    state["payment_id"] = payment_id

    assert payment_id is not None

    cur.execute("""
        SELECT customer_id, amount_cents, status, payment_method_id
        FROM payments
        WHERE id = %s
    """, (payment_id,))
    customer_id, amount_cents, status, payment_method_id = cur.fetchone()

    assert customer_id == state["guest_id"]
    assert payment_method_id == state["payment_method_id"]
    assert amount_cents == state["expected_total_cents"]
    assert status == "open"


# 19. System links payment to booking
# Related tables:
# bookings(id, payment_id)
# payments(id) referenced by bookings.payment_id
# Test steps:
# - Update the booking and set payment_id to the created payment id.
# - Select the booking again by id.
# - Assert that booking.payment_id equals the payment id.
# - Join bookings with payments.
# - Assert that the linked payment belongs to the same guest/customer.
def test_19_system_links_payment_to_booking(conn, state):
    cur = conn.cursor()

    cur.execute("""
        UPDATE bookings
        SET payment_id = %s
        WHERE id = %s
    """, (state["payment_id"], state["booking_id"]))

    cur.execute("""
        SELECT payment_id
        FROM bookings
        WHERE id = %s
    """, (state["booking_id"],))
    payment_id = cur.fetchone()[0]

    assert payment_id == state["payment_id"]

    cur.execute("""
        SELECT b.guest_account_id, p.customer_id
        FROM bookings b
        JOIN payments p ON p.id = b.payment_id
        WHERE b.id = %s
    """, (state["booking_id"],))
    guest_account_id, customer_id = cur.fetchone()

    assert guest_account_id == state["guest_id"]
    assert customer_id == state["guest_id"]


# 20. System updates payment status to payed
# Related table:
# payments(id, status)
# Test steps:
# - Update the payment status from 'open' to 'payed'.
# - Select the payment again by id.
# - Assert that status equals 'payed'.
# - Optionally assert that amount_cents did not change during the status update.
def test_20_system_updates_payment_status_to_payed(conn, state):
    cur = conn.cursor()

    cur.execute("""
        UPDATE payments
        SET status = 'payed'
        WHERE id = %s
    """, (state["payment_id"],))

    cur.execute("""
        SELECT status, amount_cents
        FROM payments
        WHERE id = %s
    """, (state["payment_id"],))
    status, amount_cents = cur.fetchone()

    assert status == "payed"
    assert amount_cents == state["expected_total_cents"]


# 21. System updates booking status to confirmed
# Related table:
# bookings(id, status)
# Test steps:
# - Update the booking status from 'pending' to 'confirmed'.
# - Select the booking again by id.
# - Assert that status equals 'confirmed'.
# - Optionally assert that payment_id is not NULL before confirming the booking.

def test_21_system_updates_booking_status_to_confirmed(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT payment_id
        FROM bookings
        WHERE id = %s
    """, (state["booking_id"],))
    payment_id = cur.fetchone()[0]

    assert payment_id is not None

    cur.execute("""
        UPDATE bookings
        SET status = 'confirmed'
        WHERE id = %s
    """, (state["booking_id"],))

    cur.execute("""
        SELECT status
        FROM bookings
        WHERE id = %s
    """, (state["booking_id"],))
    status = cur.fetchone()[0]

    assert status == "confirmed"


# 22. System checks booking status is confirmed
# Related table:
# bookings(id, status)
# Test steps:
# - Select status from bookings using the booking id.
# - Assert that the booking exists.
# - Assert that status equals 'confirmed'.
# - Optionally assert that the booking is still linked to the correct guest and accommodation.

def test_22_system_checks_booking_status_is_confirmed(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT id, guest_account_id, accommodation_id, status
        FROM bookings
        WHERE id = %s
    """, (state["booking_id"],))
    booking_id, guest_account_id, accommodation_id, status = cur.fetchone()

    assert booking_id == state["booking_id"]
    assert guest_account_id == state["guest_id"]
    assert accommodation_id == state["accommodation_id"]
    assert status == "confirmed"


# 23. System checks payment status is payed
# Related table:
# payments(id, status)
# Test steps:
# - Select status from payments using the payment id.
# - Assert that the payment exists.
# - Assert that status equals 'payed'.
# - Optionally join bookings and payments to assert that the confirmed booking uses this payed payment.
def test_23_system_checks_payment_status_is_payed(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT id, status
        FROM payments
        WHERE id = %s
    """, (state["payment_id"],))
    payment_id, status = cur.fetchone()

    assert payment_id == state["payment_id"]
    assert status == "payed"

    cur.execute("""
        SELECT b.payment_id, p.status
        FROM bookings b
        JOIN payments p ON p.id = b.payment_id
        WHERE b.id = %s
    """, (state["booking_id"],))
    linked_payment_id, linked_payment_status = cur.fetchone()

    assert linked_payment_id == state["payment_id"]
    assert linked_payment_status == "payed"


# 24. Optional: System blocks booked dates in accommodation_calendar
# Related table:
# accommodation_calendar(accommodation_id, day, is_blocked, price_addition_cents, min_nights)
# Test steps:
# - Update all calendar rows in the booked date range and set is_blocked = TRUE.
# - Select the same date range again.
# - Assert that all selected dates now have is_blocked = TRUE.
# - Query available dates for the same range.
# - Assert that the booked date range is no longer returned as available.
def test_24_system_blocks_booked_dates_in_calendar(conn, state):
    cur = conn.cursor()

    cur.execute("""
        UPDATE accommodation_calendar
        SET is_blocked = TRUE
        WHERE accommodation_id = %s
          AND day >= %s
          AND day < %s
    """, (
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))

    cur.execute("""
        SELECT COUNT(*)
        FROM accommodation_calendar
        WHERE accommodation_id = %s
          AND day >= %s
          AND day < %s
          AND is_blocked = TRUE
    """, (
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))
    blocked_count = cur.fetchone()[0]

    assert blocked_count == state["booking_nights"]

    cur.execute("""
        SELECT COUNT(*)
        FROM accommodation_calendar
        WHERE accommodation_id = %s
          AND day >= %s
          AND day < %s
          AND is_blocked = FALSE
    """, (
        state["accommodation_id"],
        state["booking_start_date"],
        state["booking_end_date"],
    ))
    available_count = cur.fetchone()[0]

    assert available_count == 0


# 25. Optional: Guest sends message to host through conversations and messages
# Related tables:
# conversations(id, created_at)
# messages(id, sender_id, receiver_id, conversation_id, body, sent_at, is_read)
# accounts(id) referenced by messages.sender_id
# accounts(id) referenced by messages.receiver_id
# conversations(id) referenced by messages.conversation_id
# Test steps:
# - Insert one conversation.
# - Store the returned conversation id.
# - Insert one message from guest to host using sender_id, receiver_id, conversation_id, and body.
# - Store the returned message id.
# - Select the message again by id.
# - Assert that sender_id equals the guest id.
# - Assert that receiver_id equals the host id.
# - Assert that conversation_id equals the created conversation id.
# - Assert that body matches the inserted text.
# - Assert that is_read is FALSE by default.
def test_25_guest_sends_message_to_host(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO conversations DEFAULT VALUES
        RETURNING id
    """)
    conversation_id = cur.fetchone()[0]
    state["conversation_id"] = conversation_id

    cur.execute("""
        INSERT INTO messages (sender_id, receiver_id, conversation_id, body)
        VALUES (%s, %s, %s, 'Hello, I am looking forward to my stay.')
        RETURNING id
    """, (state["guest_id"], state["host_id"], conversation_id))
    message_id = cur.fetchone()[0]
    state["message_id"] = message_id

    cur.execute("""
        SELECT sender_id, receiver_id, conversation_id, body, is_read
        FROM messages
        WHERE id = %s
    """, (message_id,))
    sender_id, receiver_id, selected_conversation_id, body, is_read = cur.fetchone()

    assert sender_id == state["guest_id"]
    assert receiver_id == state["host_id"]
    assert selected_conversation_id == conversation_id
    assert body == "Hello, I am looking forward to my stay."
    assert is_read is False


# 26. Optional: System creates notification for host/customer
# Related table:
# notifications(id, account_id, payload, sent_at)
# accounts(id) referenced by notifications.account_id
# Test steps:
# - Insert one notification for the host or guest account.
# - Store the returned notification id.
# - Select the notification again by id.
# - Assert that account_id equals the expected receiver account id.
# - Assert that payload contains the expected event type, e.g. booking_confirmed.
# - Assert that sent_at is not NULL.
def test_26_system_creates_notification_for_host(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO notifications (account_id, payload)
        VALUES (%s, '{"type":"booking_confirmed"}')
        RETURNING id
    """, (state["host_id"],))
    notification_id = cur.fetchone()[0]
    state["notification_id"] = notification_id

    cur.execute("""
        SELECT account_id, payload, sent_at
        FROM notifications
        WHERE id = %s
    """, (notification_id,))
    account_id, payload, sent_at = cur.fetchone()

    assert account_id == state["host_id"]
    assert payload["type"] == "booking_confirmed"
    assert sent_at is not None


# 27. After stay: system updates booking status to completed
# Related table:
# bookings(id, status)
# Test steps:
# - Update the booking status from 'confirmed' to 'completed'.
# - Select the booking again by id.
# - Assert that status equals 'completed'.
# - Optionally assert that payment status is still 'payed'.
def test_27_system_updates_booking_status_to_completed(conn, state):
    cur = conn.cursor()

    cur.execute("""
        UPDATE bookings
        SET status = 'completed'
        WHERE id = %s
    """, (state["booking_id"],))

    cur.execute("""
        SELECT b.status, p.status
        FROM bookings b
        JOIN payments p ON p.id = b.payment_id
        WHERE b.id = %s
    """, (state["booking_id"],))
    booking_status, payment_status = cur.fetchone()

    assert booking_status == "completed"
    assert payment_status == "payed"


# 28. Guest creates review for accommodation
# Related table:
# reviews(id, accommodation_id, author_account_id, rating, description, created_at)
# accommodations(id) referenced by reviews.accommodation_id
# accounts(id) referenced by reviews.author_account_id
# Test steps:
# - Insert one review using the accommodation id and guest id.
# - Use a valid rating between 1 and 5.
# - Store the returned review id.
# - Select the review again by id.
# - Assert that accommodation_id equals the booked accommodation id.
# - Assert that author_account_id equals the guest id.
# - Assert that rating and description match the inserted values.
# - Assert that created_at is not NULL.
def test_28_guest_creates_review_for_accommodation(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO reviews (accommodation_id, author_account_id, rating, description)
        VALUES (%s, %s, 5, 'Excellent stay and smooth booking process.')
        RETURNING id
    """, (state["accommodation_id"], state["guest_id"]))
    review_id = cur.fetchone()[0]
    state["review_id"] = review_id

    assert review_id is not None

    cur.execute("""
        SELECT accommodation_id, author_account_id, rating, description, created_at
        FROM reviews
        WHERE id = %s
    """, (review_id,))
    accommodation_id, author_account_id, rating, description, created_at = cur.fetchone()

    assert accommodation_id == state["accommodation_id"]
    assert author_account_id == state["guest_id"]
    assert rating == 5
    assert description == "Excellent stay and smooth booking process."
    assert created_at is not None


# 29. Optional: Guest attaches review image
# Related tables:
# review_images(review_id, image_id)
# reviews(id) referenced by review_images.review_id
# images(id) referenced by review_images.image_id
# Test steps:
# - Insert one image record for the review image.
# - Store the returned image id.
# - Insert one row into review_images using the review id and image id.
# - Select the review image through a JOIN from review_images to images.
# - Assert that review_id equals the created review id.
# - Assert that image_id equals the created image id.
# - Assert that the expected storage_key is returned.
def test_29_guest_attaches_review_image(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO images (mime, storage_key)
        VALUES ('image/jpeg', 'business_logic_review_image.jpg')
        RETURNING id
    """)
    review_image_id = cur.fetchone()[0]
    state["review_image_id"] = review_image_id

    cur.execute("""
        INSERT INTO review_images (review_id, image_id)
        VALUES (%s, %s)
    """, (state["review_id"], review_image_id))

    cur.execute("""
        SELECT ri.review_id, ri.image_id, i.storage_key
        FROM review_images ri
        JOIN images i ON i.id = ri.image_id
        WHERE ri.review_id = %s
    """, (state["review_id"],))
    review_id, image_id, storage_key = cur.fetchone()

    assert review_id == state["review_id"]
    assert image_id == review_image_id
    assert storage_key == "business_logic_review_image.jpg"


# 30. System verifies review is linked to correct accommodation and guest
# Related tables:
# reviews(id, accommodation_id, author_account_id, rating, description, created_at)
# accommodations(id)
# accounts(id)
# Test steps:
# - Join reviews with accommodations and accounts.
# - Select the review using the review id.
# - Assert that the accommodation title matches the booked accommodation.
# - Assert that the author email matches the guest email.
# - Assert that the rating matches the inserted review rating.
# - Optionally assert that the reviewed accommodation is the same one from the completed booking.
def test_30_system_verifies_review_is_linked_correctly(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT r.accommodation_id, r.author_account_id, r.rating, a.title, acc.email
        FROM reviews r
        JOIN accommodations a ON a.id = r.accommodation_id
        JOIN accounts acc ON acc.id = r.author_account_id
        WHERE r.id = %s
    """, (state["review_id"],))
    accommodation_id, author_account_id, rating, accommodation_title, author_email = cur.fetchone()

    assert accommodation_id == state["accommodation_id"]
    assert author_account_id == state["guest_id"]
    assert rating == 5
    assert accommodation_title == "Business Logic Apartment"
    assert author_email == "guest@test.com"


# 31. Optional: Host payout account exists
# Related table:
# payout_accounts(id, host_account_id, type, is_default)
# accounts(id) referenced by payout_accounts.host_account_id
# Test steps:
# - Insert one payout account for the host account.
# - Use type = 'card' or type = 'paypal'.
# - Set is_default = TRUE.
# - Store the returned payout_account id.
# - Select the payout account again by id.
# - Assert that host_account_id equals the host id.
# - Assert that type matches the inserted payout account type.
# - Assert that is_default is TRUE.
def test_31_host_payout_account_exists(conn, state):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payout_accounts (host_account_id, type, is_default)
        VALUES (%s, 'card', TRUE)
        RETURNING id
    """, (state["host_id"],))
    payout_account_id = cur.fetchone()[0]
    state["payout_account_id"] = payout_account_id

    assert payout_account_id is not None

    cur.execute("""
        SELECT host_account_id, type, is_default
        FROM payout_accounts
        WHERE id = %s
    """, (payout_account_id,))
    host_account_id, payout_type, is_default = cur.fetchone()

    assert host_account_id == state["host_id"]
    assert payout_type == "card"
    assert is_default is True


# 32. Optional: System creates payout for completed booking
# Related table:
# payouts(id, host_account_id, payout_account_id, booking_id, amount_cents, currency, status)
# accounts(id) referenced by payouts.host_account_id
# payout_accounts(id) referenced by payouts.payout_account_id
# bookings(id) referenced by payouts.booking_id
# Test steps:
# - Insert one payout using the host id, payout_account id, and completed booking id.
# - Use a positive amount_cents value.
# - Set currency = 'EUR'.
# - Set status to a business value such as 'open', 'scheduled', or 'completed'.
# - Store the returned payout id.
# - Select the payout again by id.
# - Assert that host_account_id equals the host id.
# - Assert that payout_account_id equals the created payout account id.
# - Assert that booking_id equals the completed booking id.
# - Assert that amount_cents matches the expected payout amount.
# - Assert that currency equals 'EUR'.
# - Assert that status matches the inserted payout status.
def test_32_system_creates_payout_for_completed_booking(conn, state):
    cur = conn.cursor()

    payout_amount_cents = int(state["expected_total_cents"] * 0.85)
    state["payout_amount_cents"] = payout_amount_cents

    cur.execute("""
        INSERT INTO payouts (
            host_account_id, payout_account_id, booking_id, amount_cents, currency, status
        )
        VALUES (%s, %s, %s, %s, 'EUR', 'scheduled')
        RETURNING id
    """, (
        state["host_id"],
        state["payout_account_id"],
        state["booking_id"],
        payout_amount_cents,
    ))
    payout_id = cur.fetchone()[0]
    state["payout_id"] = payout_id

    assert payout_id is not None

    cur.execute("""
        SELECT host_account_id, payout_account_id, booking_id, amount_cents, currency, status
        FROM payouts
        WHERE id = %s
    """, (payout_id,))
    host_account_id, payout_account_id, booking_id, amount_cents, currency, status = cur.fetchone()

    assert host_account_id == state["host_id"]
    assert payout_account_id == state["payout_account_id"]
    assert booking_id == state["booking_id"]
    assert amount_cents == payout_amount_cents
    assert currency == "EUR"
    assert status == "scheduled"


# 33. Final assertion: booking, payment, accommodation, review, and customer records are correctly connected through joins.
# Related tables:
# bookings(id, guest_account_id, accommodation_id, payment_id, status)
# payments(id, customer_id, amount_cents, status, payment_method_id)
# payment_methods(id, customer_id, type)
# accommodations(id, host_account_id, title, price_cents)
# reviews(id, accommodation_id, author_account_id, rating)
# accounts(id, email, role)
# Test steps:
# - Join bookings with guest account, accommodation, host account, payment, payment method, and review.
# - Select the full customer journey row using the booking id.
# - Assert that the guest account id equals bookings.guest_account_id.
# - Assert that the host account id equals accommodations.host_account_id.
# - Assert that payment id equals bookings.payment_id.
# - Assert that payment customer_id equals the guest id.
# - Assert that payment_method customer_id equals the guest id.
# - Assert that review accommodation_id equals the booked accommodation id.
# - Assert that review author_account_id equals the guest id.
# - Assert that booking status equals 'completed'.
# - Assert that payment status equals 'payed'.
# - Assert that accommodation title, price, guest email, host email, payment amount, and review rating match the expected values.
def test_33_final_customer_journey_join_assertion(conn, state):
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.id,
            b.guest_account_id,
            b.accommodation_id,
            b.payment_id,
            b.status,
            p.customer_id,
            p.amount_cents,
            p.status,
            pm.customer_id,
            pm.type,
            a.host_account_id,
            a.title,
            a.price_cents,
            r.accommodation_id,
            r.author_account_id,
            r.rating,
            guest.email,
            guest.role,
            host.email,
            host.role
        FROM bookings b
        JOIN payments p ON p.id = b.payment_id
        JOIN payment_methods pm ON pm.id = p.payment_method_id
        JOIN accommodations a ON a.id = b.accommodation_id
        JOIN reviews r ON r.accommodation_id = a.id
        JOIN accounts guest ON guest.id = b.guest_account_id
        JOIN accounts host ON host.id = a.host_account_id
        WHERE b.id = %s
          AND r.id = %s
    """, (state["booking_id"], state["review_id"]))
    row = cur.fetchone()

    assert row is not None

    (
        booking_id,
        booking_guest_id,
        booking_accommodation_id,
        booking_payment_id,
        booking_status,
        payment_customer_id,
        payment_amount_cents,
        payment_status,
        payment_method_customer_id,
        payment_method_type,
        accommodation_host_id,
        accommodation_title,
        accommodation_price_cents,
        review_accommodation_id,
        review_author_id,
        review_rating,
        guest_email,
        guest_role,
        host_email,
        host_role,
    ) = row

    assert booking_id == state["booking_id"]
    assert booking_guest_id == state["guest_id"]
    assert booking_accommodation_id == state["accommodation_id"]
    assert booking_payment_id == state["payment_id"]
    assert payment_customer_id == state["guest_id"]
    assert payment_method_customer_id == state["guest_id"]
    assert accommodation_host_id == state["host_id"]
    assert review_accommodation_id == state["accommodation_id"]
    assert review_author_id == state["guest_id"]
    assert booking_status == "completed"
    assert payment_status == "payed"
    assert payment_method_type == "card"
    assert accommodation_title == "Business Logic Apartment"
    assert accommodation_price_cents == state["base_price_cents"]
    assert payment_amount_cents == state["expected_total_cents"]
    assert review_rating == 5
    assert guest_email == "guest@test.com"
    assert guest_role == "guest"
    assert host_email == "host@test.com"
    assert host_role == "host"