-- 01_schema.sql
-- Schema definition derived from Data Description Table

-- ENUM TYPES
CREATE TYPE role AS ENUM ('guest', 'host', 'admin');
CREATE TYPE payment_method_type AS ENUM ('card', 'paypal');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'cancelled', 'completed');

-- CORE TABLES
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role role NOT NULL DEFAULT 'guest',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE credentials (
    account_id INT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
    password_hash TEXT NOT NULL,
    password_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    line1 VARCHAR(255) NOT NULL,
    line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL
);

-- ACCOMMODATIONS + RELATIONS
CREATE TABLE amenities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50)
);

CREATE TABLE accommodations (
    id SERIAL PRIMARY KEY,
    host_account_id INT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    address_id INT REFERENCES addresses(id),
    price_cents INT NOT NULL CHECK (price_cents >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accommodation_amenities (
    accommodation_id INT NOT NULL REFERENCES accommodations(id) ON DELETE CASCADE,
    amenity_id INT NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    PRIMARY KEY (accommodation_id, amenity_id)
);

CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    mime VARCHAR(100) NOT NULL,
    storage_key VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accommodation_images (
    accommodation_id INT NOT NULL REFERENCES accommodations(id) ON DELETE CASCADE,
    image_id INT NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    sort_order INT,
    is_cover BOOLEAN DEFAULT FALSE,
    caption VARCHAR(255),
    room_tag VARCHAR(100),
    PRIMARY KEY (accommodation_id, image_id)
);

CREATE TABLE accommodation_calendar (
    accommodation_id INT NOT NULL REFERENCES accommodations(id) ON DELETE CASCADE,
    day DATE NOT NULL,
    is_blocked BOOLEAN DEFAULT FALSE,
    price_cents INT,
    min_nights INT DEFAULT 1,
    PRIMARY KEY (accommodation_id, day)
);

-- BOOKINGS + REVIEWS
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES accounts(id),
    amount_cents INT CHECK (amount_cents >= 0),
    status VARCHAR(50),
    payment_method_id INT
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    guest_account_id INT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    accommodation_id INT NOT NULL REFERENCES accommodations(id) ON DELETE CASCADE,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    payment_id INT REFERENCES payments(id),
    status booking_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    accommodation_id INT NOT NULL REFERENCES accommodations(id) ON DELETE CASCADE,
    author_account_id INT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE review_images (
    review_id INT NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    k INT NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    PRIMARY KEY (review_id, image_id)
);

-- MESSAGING SYSTEM
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES accounts(id) ON DELETE CASCADE,
    receiver_id INT REFERENCES accounts(id) ON DELETE CASCADE,
    conversation_id INT REFERENCES conversations(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);

-- PAYMENTS + METHODS
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES accounts(id),
    type payment_method_type NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE credit_cards (
    id SERIAL PRIMARY KEY,
    payment_method_id INT UNIQUE REFERENCES payment_methods(id) ON DELETE CASCADE,
    brand VARCHAR(50),
    last4 VARCHAR(4),
    exp_month INT CHECK (exp_month BETWEEN 1 AND 12),
    exp_year INT
);

CREATE TABLE paypal (
    id SERIAL PRIMARY KEY,
    payment_method_id INT UNIQUE REFERENCES payment_methods(id) ON DELETE CASCADE,
    paypal_user_id VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

ALTER TABLE payments
    ADD FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id) ON DELETE SET NULL;

-- PAYOUTS + NOTIFICATIONS
CREATE TABLE payout_accounts (
    id SERIAL PRIMARY KEY,
    host_account_id INT REFERENCES accounts(id),
    type payment_method_type,
    is_default BOOLEAN DEFAULT FALSE
);

CREATE TABLE payouts (
    id SERIAL PRIMARY KEY,
    host_account_id INT REFERENCES accounts(id),
    payout_account_id INT REFERENCES payout_accounts(id),
    booking_id INT REFERENCES bookings(id),
    amount_cents INT CHECK (amount_cents >= 0),
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(50)
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(id),
    payload JSON,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);