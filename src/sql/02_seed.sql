-- ============================================
-- 02_seed.sql
-- Purpose: Insert static lookup data and initial configuration
-- ============================================

INSERT INTO roles (role_name) VALUES
  ('admin'),
  ('host'),
  ('guest');

INSERT INTO payment_status (status_name) VALUES
  ('pending'),
  ('paid'),
  ('cancelled');