-- DROP TABLES (Safe for dev resets)
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS hotel_rooms CASCADE;
DROP TABLE IF EXISTS hotels CASCADE;
 
-- ENUM for room type
-- CREATE TYPE room_type_enum AS ENUM ('single', 'double', 'suite', 'deluxe', 'presidential');
 
-- HOTELS
CREATE TABLE hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address TEXT,
    stars INTEGER CHECK (stars >= 1 AND stars <= 5) NOT NULL,
    description TEXT,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    amenities TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    -- CONSTRAINTS
    CONSTRAINT valid_email CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_phone CHECK (phone_number ~ '^\+?[0-9\s\-()]{7,20}$')
);
 
-- ROOMS
CREATE TYPE room_type_enum AS ENUM ('single', 'double', 'suite', 'family');
CREATE TABLE hotel_rooms (
    id SERIAL PRIMARY KEY,
    hotel_id INTEGER NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    room_number VARCHAR(10) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0 AND capacity <= 10),
    price_per_night DECIMAL(10,2) NOT NULL CHECK (price_per_night > 0),
    room_type room_type_enum NOT NULL DEFAULT 'single',
    is_available BOOLEAN DEFAULT TRUE,
    image_urls TEXT[],
    amenities TEXT[],
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hotel_id, room_number)
);
 
-- BOOKINGS
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES hotel_rooms(id) ON DELETE CASCADE,
    guest_name VARCHAR(255) NOT NULL,
    guest_email VARCHAR(255),
    guest_phone VARCHAR(20),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled', 'completed')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
 
    CONSTRAINT valid_dates CHECK (check_out > check_in),
    CONSTRAINT valid_guest_email CHECK (guest_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_guest_phone CHECK (guest_phone ~ '^\+?[0-9\s\-()]{7,20}$')
);
 
-- INDEXES
CREATE INDEX idx_hotels_city ON hotels(city);
CREATE INDEX idx_hotels_stars ON hotels(stars);
CREATE INDEX idx_hotels_active ON hotels(is_active);
CREATE INDEX idx_hotel_rooms_hotel_id ON hotel_rooms(hotel_id);
CREATE INDEX idx_hotel_rooms_available ON hotel_rooms(is_available);
CREATE INDEX idx_hotel_rooms_price ON hotel_rooms(price_per_night);
CREATE INDEX idx_hotel_rooms_type ON hotel_rooms(room_type);
CREATE INDEX idx_bookings_room_id ON bookings(room_id);
CREATE INDEX idx_bookings_dates ON bookings(check_in, check_out);
CREATE INDEX idx_bookings_status ON bookings(status);
 
-- AUTO TIMESTAMP FUNCTION
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 
-- TRIGGERS
CREATE TRIGGER update_hotels_updated_at BEFORE UPDATE ON hotels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
 
CREATE TRIGGER update_hotel_rooms_updated_at BEFORE UPDATE ON hotel_rooms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
 
CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
 
 
 
INSERT INTO hotels (
    name, city, address, stars, description, phone_number, email, latitude, longitude, amenities
)
VALUES
    ('Pearl Continental', 'Lahore', 'Mall Road, Lahore', 5, 'Luxury hotel in Lahore', '+92-42-111-505-505', 'pc@hotel.com', 31.5497, 74.3436, ARRAY['WiFi', 'Gym', 'Pool']),
    ('Avari Towers', 'Karachi', 'Fatima Jinnah Road', 5, 'Business hotel with sea view', '+92-21-3566-0100', 'avari@hotel.com', 24.8607, 67.0011, ARRAY['WiFi', 'Spa', 'Restaurant']),
    ('Serena Hotel', 'Islamabad', 'Khayaban-e-Suhrawardy', 5, 'Serene location with luxury', '+92-51-111-133-133', 'serena@hotel.com', 33.6844, 73.0479, ARRAY['WiFi', 'Pool', 'Spa']),
    ('Hotel One', 'Multan', 'Boson Road', 3, 'Budget-friendly and comfortable', '+92-61-111-000-011', 'hotelone@hotel.com', 30.1575, 71.5249, ARRAY['WiFi', 'Parking']),
    ('The Nishat Hotel', 'Lahore', 'Gulberg III', 4, 'Stylish boutique hotel', '+92-42-111-222-333', 'nishat@hotel.com', 31.5204, 74.3587, ARRAY['WiFi', 'Restaurant']),
    ('Marriott Hotel', 'Islamabad', 'Aga Khan Road', 5, 'Luxury with business facilities', '+92-51-282-6121', 'marriott@hotel.com', 33.6938, 73.0652, ARRAY['WiFi', 'Conference Rooms']),
    ('Beach Luxury', 'Karachi', 'M.T. Khan Road', 4, 'Affordable seaside stay', '+92-21-3561-2233', 'beachlux@hotel.com', 24.8435, 66.9986, ARRAY['WiFi', 'Sea View']),
    ('Faletti''s Hotel', 'Lahore', 'Egor Road', 4, 'Heritage and elegance combined', '+92-42-3630-0000', 'faletti@hotel.com', 31.5690, 74.3142, ARRAY['WiFi', 'Parking']),
    ('PC Bhurban', 'Murree', 'Bhurban Road', 5, 'Hillside luxury resort', '+92-51-335-5701', 'bhurban@pc.com', 33.9716, 73.3969, ARRAY['WiFi', 'Nature Walks']),
    ('City Hotel', 'Faisalabad', 'Susan Road', 3, 'Affordable city hotel', '+92-41-871-0000', 'city@hotel.com', 31.4180, 73.0791, ARRAY['WiFi']);

 
 
ALTER TYPE room_type_enum ADD VALUE IF NOT EXISTS 'deluxe';
INSERT INTO hotel_rooms (hotel_id, room_number, capacity, price_per_night, room_type, is_available, image_urls, amenities)
SELECT 
    h.id,
    'R' || gs || '-H' || h.id,
    (1 + (RANDOM() * 5)::INT),
    ROUND((RANDOM() * 200 + 50)::NUMERIC, 2),
    CASE 
        WHEN gs % 5 = 0 THEN 'suite'
        WHEN gs % 4 = 0 THEN 'deluxe'
        WHEN gs % 3 = 0 THEN 'double'
        ELSE 'single'
    END::room_type_enum,
    (RANDOM() > 0.25),
    ARRAY['https://example.com/room' || gs || '.jpg'],
    ARRAY['WiFi', 'TV', 'Mini Bar']
FROM hotels h
CROSS JOIN generate_series(1, 5) AS gs;
 
 
 
-- INSERT INTO bookings (room_id, guest_name, guest_email, guest_phone, check_in, check_out, total_amount, status)
-- SELECT 
--     hr.id,
--     'Guest ' || hr.id,
--     'guest' || hr.id || '@example.com',
--     '+92-3' || LPAD((RANDOM() * 9999999)::TEXT, 7, '0'),
--     CURRENT_DATE + (RANDOM() * 5)::INT,
--     CURRENT_DATE + 5 + (RANDOM() * 5)::INT,
--     ROUND(hr.price_per_night * (2 + (RANDOM() * 3)::INT), 2),
--     'confirmed'
-- FROM hotel_rooms hr
-- WHERE RANDOM() < 0.2
-- AND hr.is_available = TRUE;
 
 
INSERT INTO bookings (room_id, guest_name, guest_email, guest_phone, check_in, check_out, total_amount, status)
SELECT 
    hr.id,
    'Guest ' || hr.id,
    'guest' || hr.id || '@example.com',
    '+92-3' || LPAD((FLOOR(RANDOM() * 9999999))::TEXT, 7, '0'),
    CURRENT_DATE + (RANDOM() * 5)::INT,
    CURRENT_DATE + 5 + (RANDOM() * 5)::INT,
    ROUND(hr.price_per_night * (2 + (RANDOM() * 3)::INT), 2),
    'confirmed'
FROM hotel_rooms hr
WHERE RANDOM() < 0.2
AND hr.is_available = TRUE;
 
 
UPDATE hotel_rooms 
SET is_available = FALSE
WHERE id IN (
    SELECT DISTINCT room_id 
    FROM bookings 
    WHERE status = 'confirmed' 
    AND check_out >= CURRENT_DATE
);
SELECT * FROM hotel_rooms;