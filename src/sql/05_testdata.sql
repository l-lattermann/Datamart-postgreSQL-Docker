-- ============================================
-- 05_testdata.sql
-- Purpose: Insert sample data for development/testing
-- ============================================

INSERT INTO users (username, email) VALUES
  ('alice', 'alice@example.com'),
  ('bob', 'bob@example.com');

INSERT INTO bookings (user_id, check_in, check_out, total_price) VALUES
  (1, '2025-11-01', '2025-11-03', 240.00),
  (2, '2025-11-05', '2025-11-10', 600.00);