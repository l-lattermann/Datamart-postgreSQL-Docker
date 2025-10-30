-- ============================================
-- 04_functions.sql
-- Purpose: Business logic inside the database
-- ============================================

-- Function to calculate booking duration
CREATE OR REPLACE FUNCTION booking_duration(start_date DATE, end_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN end_date - start_date;
END;
$$ LANGUAGE plpgsql;

-- Trigger example
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();