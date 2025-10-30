-- ============================================
-- 03_indexes.sql
-- Purpose: Define performance indexes and derived views
-- ============================================

-- Performance indexes
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_date_range ON bookings(check_in, check_out);

-- Example view
CREATE VIEW active_users AS
SELECT user_id, username, email
FROM users
WHERE is_active = TRUE;