# Technical Specification: Data Normalization Engine

## 1. System Architecture
* **Stack:** Python 3.11, FastAPI, Uvicorn, Pillow, piexif.
* **Purpose:** To normalize image headers and binary data for testing environments.

## 2. Logic Specifications

### A. Location Fuzzing Module (`utils.py`)
* **Purpose:** Protect exact user location via randomization.
* **Input:** `base_lat`, `base_lon`
* **Logic:**
    * Apply uniform random delta: `offset = random.uniform(-0.00005, 0.00005)`
    * Result: `target = base + offset`
    * Convert to EXIF Rational Format (DMS).

### B. Timestamp Simulation Module (`utils.py`)
* **Purpose:** Simulate historical data ingestion.
* **Logic:**
    * Generate a timestamp for a past window: `current_time - random.randint(3, 7) days`.
    * Set time to business hours (09:00-21:00) to simulate active user windows.
    * Format: `%Y:%m:%d %H:%M:%S`

### C. Reference Metadata Injection (`utils.py`)
* **Purpose:** Standardize output to match "Samsung Galaxy S24 Ultra" specifications for compatibility testing.
* **Tags to Set:**
    * `Make`: "Samsung"
    * `Model`: "SM-S928N"
    * `Software`: "S928NKSU1BWK7"
    * `FocalLength`, `FNumber`, `ISOSpeedRatings`: Set to fixed reference values.

### D. Unique Identifier Generation (`utils.py`)
* **Purpose:** Prevent hash collisions in the database.
* **Logic:**
    * Load image.
    * Select 5 random pixels.
    * Adjust Blue channel by ±1 (imperceptible change).
    * Save to stream.

## 3. API Endpoint (`POST /normalize`)
* **Input:** Image File, Latitude, Longitude, Address Text (for `UserComment`).
* **Process:** Strip original Exif -> Apply Fuzzing -> Inject Reference Metadata -> Apply Hash modification -> Return Binary.
* **Output:** JPEG File stream.