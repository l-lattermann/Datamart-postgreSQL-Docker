-- ============================================
-- 02_seed.sql
-- Purpose: Insert static lookup data and initial configuration
-- ============================================

INSERT INTO amenities (name, category) VALUES
('Free WiFi', 'Internet'),
('Swimming Pool', 'Recreation'),
('Fitness Center', 'Recreation'),
('Spa', 'Wellness'),
('Restaurant', 'Dining'),
('Bar', 'Dining'),
('Room Service', 'Service'),
('Laundry Service', 'Service'),
('Airport Shuttle', 'Transport'),
('Parking', 'Transport'),
('Pet Friendly', 'Policy'),
('24-Hour Front Desk', 'Service'),
('Business Center', 'Business'),
('Conference Rooms', 'Business'),
('Non-Smoking Rooms', 'Policy'),
('Air Conditioning', 'Comfort'),
('Heating', 'Comfort'),
('Flat-Screen TV', 'Entertainment'),
('Mini Bar', 'Dining'),
('In-Room Safe', 'Security');