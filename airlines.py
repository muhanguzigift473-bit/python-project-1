import sqlite3

# 1. Connect to the aviation database (creates 'airport.db' file)
conn = sqlite3.connect('airport.db')
cursor = conn.cursor()

# Enforce foreign key constraints in SQLite
cursor.execute("PRAGMA foreign_keys = ON;")

# 2. Create Tables
# Table A: Airlines
cursor.execute('''
CREATE TABLE IF NOT EXISTS airlines (
    airline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airline_code TEXT UNIQUE NOT NULL, -- e.g., 'EK', 'DL'
    airline_name TEXT NOT NULL,
    country_of_origin TEXT
)
''')

# Table B: Destinations (Airports)
cursor.execute('''
CREATE TABLE IF NOT EXISTS destinations (
    airport_code TEXT PRIMARY KEY, -- e.g., 'DXB', 'JFK'
    airport_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL
)
''')

# Table C: Route Details (Links Airlines and Destinations)
cursor.execute('''
CREATE TABLE IF NOT EXISTS routes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT UNIQUE NOT NULL, -- e.g., 'EK072'
    airline_id INTEGER,
    origin_airport TEXT NOT NULL,
    destination_airport TEXT,
    ticket_price REAL CHECK(ticket_price > 0),
    FOREIGN KEY (airline_id) REFERENCES airlines(airline_id),
    FOREIGN KEY (destination_airport) REFERENCES destinations(airport_code)
)
''')

# 3. Clear existing data to ensure a fresh run
cursor.execute("DELETE FROM routes")
cursor.execute("DELETE INDEX IF EXISTS airlines")
cursor.execute("DELETE FROM airlines")
cursor.execute("DELETE FROM destinations")

# 4. Insert Sample Data
# Populate Airlines
airlines_data = [
    ('EK', 'Emirates', 'United Arab Emirates'),
    ('QR', 'Qatar Airways', 'Qatar'),
    ('UR', 'Uganda Airlines', 'Uganda'),
    ('DL', 'Delta Air Lines', 'United States')
]
cursor.executemany("INSERT INTO airlines (airline_code, airline_name, country_of_origin) VALUES (?, ?, ?)", airlines_data)

# Populate Destinations
destinations_data = [
    ('DXB', 'Dubai International Airport', 'Dubai', 'UAE'),
    ('DOH', 'Hamad International Airport', 'Doha', 'Qatar'),
    ('EBB', 'Entebbe International Airport', 'Entebbe', 'Uganda'),
    ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
    ('LHR', 'Heathrow Airport', 'London', 'UK')
]
cursor.executemany("INSERT INTO destinations (airport_code, airport_name, city, country) VALUES (?, ?, ?, ?)", destinations_data)

# Commit to get the auto-generated airline IDs safely
conn.commit()

# Populate Routes (Connecting the pieces)
routes_data = [
    ('UR412', 3, 'EBB', 'DXB', 450.00),  # Uganda Airlines: Entebbe to Dubai
    ('EK072', 1, 'DXB', 'LHR', 780.50),  # Emirates: Dubai to London Heathrow
    ('QR701', 2, 'DOH', 'JFK', 1200.00), # Qatar Airways: Doha to New York
    ('DL430', 4, 'JFK', 'LHR', 650.00)   # Delta: New York to London Heathrow
]
cursor.executemany("INSERT INTO routes (flight_number, airline_id, origin_airport, destination_airport, ticket_price) VALUES (?, ?, ?, ?, ?)", routes_data)
conn.commit()

# 5. Query the Data (Joining tables to get a clear flight schedule)
print("--- LIVE FLIGHT SCHEDULE & ROUTE DETAILS ---")
query = '''
SELECT 
    r.flight_number, 
    a.airline_name, 
    r.origin_airport, 
    d.city AS destination_city, 
    d.country AS destination_country,
    r.ticket_price
FROM routes r
JOIN airlines a ON r.airline_id = a.airline_id
JOIN destinations d ON r.destination_airport = d.airport_code
'''
cursor.execute(query)
rows = cursor.fetchall()

# Print formatted headers
print(f"{'Flight':<8} | {'Airline':<18} | {'From':<5} | {'To City':<12} | {'To Country':<12} | {'Price':<8}")
print("-" * 75)

# Print data rows
for row in rows:
    print(f"{row[0]:<8} | {row[1]:<18} | {row[2]:<5} | {row[3]:<12} | {row[4]:<12} | ${row[5]:.2f}")

# Close connection
conn.close()
