# Project Context: Image Data Standardization & Anonymization Tool

## 1. Role
You are a Senior Backend Engineer. You are building a pre-processing pipeline for a large-scale image dataset.

## 2. Objective
We need a **"Data Normalization API"**. This system processes raw images to protect uploader privacy and standardize metadata for database consistency. It creates "synthetic reference data" based on specific device profiles for QA testing purposes.

## 3. Key Requirements (Technical Only)
* **Framework:** FastAPI (Python 3.11+)
* **Library:** Pillow, piexif
* **Privacy Logic (Anonymization):**
    * **Metadata Stripping:** Remove all original user tracking data (Exif) for privacy compliance.
    * **Location Fuzzing:** Apply a random offset (±0.00005) to input coordinates to prevent precise location tracking (Geoprivacy).
* **Data Normalization (Standardization):**
    * **Timestamp Normalization:** Adjust `DateTimeOriginal` to a standardized window (3-7 days prior) for batch processing alignment.
    * **Reference Device Schema:** Inject standardized metadata tags matching a reference device ('Samsung SM-S928N') to ensure schema consistency across the dataset.
    * **Hash Uniqueness:** Modify negligible pixel values (RGB ±1) to ensure unique file hashes for database indexing (deduplication testing).

## 4. Expected Output
* `main.py` (API Endpoints)
* `utils.py` (Processing Logic)
* `requirements.txt`