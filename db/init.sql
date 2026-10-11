CREATE TABLE IF NOT EXISTS users (
 id SERIAL PRIMARY KEY, name VARCHAR(120) NOT NULL,
 email VARCHAR(255) UNIQUE NOT NULL, password_hash TEXT NOT NULL,
 created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS events (
 id SERIAL PRIMARY KEY, title VARCHAR(160) UNIQUE NOT NULL,
 description TEXT NOT NULL, venue VARCHAR(160) NOT NULL,
 event_date DATE NOT NULL, price NUMERIC(10,2) NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS bookings (
 id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 event_id INTEGER NOT NULL REFERENCES events(id), attendee_name VARCHAR(120) NOT NULL,
 age INTEGER NOT NULL CHECK(age BETWEEN 1 AND 120), email VARCHAR(255) NOT NULL,
 phone VARCHAR(30) NOT NULL, slot VARCHAR(80) NOT NULL, booked_at TIMESTAMPTZ DEFAULT NOW()
);
INSERT INTO events(title,description,venue,event_date,price) VALUES
('Chennai Music Fest','A live evening of music and performances.','YMCA Grounds, Chennai',CURRENT_DATE+14,499),
('Tech & Innovation Summit','Talks and networking with technology enthusiasts.','Chennai Trade Centre',CURRENT_DATE+21,799),
('Stand-up Comedy Night','A night of stand-up comedy and fun.','Phoenix Marketcity, Chennai',CURRENT_DATE+28,399),
('Startup Networking Meetup','Meet founders, builders, and early-career professionals.','Tidel Park, Chennai',CURRENT_DATE+35,199)
ON CONFLICT(title) DO NOTHING;
