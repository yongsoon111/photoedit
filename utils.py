import random
import string
from datetime import datetime, timedelta
from io import BytesIO
from typing import Tuple, Optional, List, Dict
import re
import requests
import zipfile
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import piexif

# ... (Existing DEVICE_POOL and rest of file above ImageProcessor) ...
# I need to be careful with the context. I'll use the provided previous content as base.
# Since I'm replacing the whole file effectively if I use replace_file_content on a large range, 
# or I can append/insert methods.
# The user wants "zip handling" and "dashboard".
# I'll add the imports and the new methods to the ImageProcessor class.

# To be safe and clean, I will read the file first to ensure I have the context correctly if I use a small edit.
# But I have the context from previous turn.
# I will insert the imports at the top and methods at the end of the class.

# Wait, `replace_file_content` is better for contiguous blocks.
# I'll do it in two chunks or one big update if I'm confident.
# Let's insert imports first, then methods.
# Actually I can just replace the whole file content if I really want to be sure, but that's expensive/risky.
# I'll just add the methods to `ImageProcessor`.

# Imports need to be at top.

# === [Detailed Device Pool - Samsung 14개 (70%) : Apple 6개 (30%)] ===
# FNumber: (numerator, denominator) e.g. (17, 10) = f/1.7
# FocalLength: (mm * 100, 100) e.g. (630, 100) = 6.3mm
# Resolution: (Width, Height) in landscape mode - 팩토리 해상도
DEVICE_POOL = [
    # === Samsung Galaxy (14개 = 70%) ===
    # S24 시리즈 (200MP main = 12MP output typically 4000x3000)
    {"Make": "Samsung", "Model": "SM-S928N", "Software": "S928NKSU1BWK7", "FNumber": (17, 10), "FocalLength": (630, 100), "LensModel": "Samsung S24 Ultra Wide Angle", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-S926N", "Software": "S926NKSU1AWK3", "FNumber": (22, 10), "FocalLength": (670, 100), "LensModel": "Samsung S24+ Main Camera", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-S921N", "Software": "S921NKSU1AWK1", "FNumber": (18, 10), "FocalLength": (670, 100), "LensModel": "Samsung S24 Main Camera", "Resolution": (4000, 3000)},
    # S23 시리즈
    {"Make": "Samsung", "Model": "SM-S918N", "Software": "S918NKSU2CWK2", "FNumber": (17, 10), "FocalLength": (630, 100), "LensModel": "Samsung S23 Ultra Wide Angle", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-S916N", "Software": "S916NKSU2BWK1", "FNumber": (22, 10), "FocalLength": (670, 100), "LensModel": "Samsung S23+ Main Camera", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-S911N", "Software": "S911NKSU2CWK1", "FNumber": (18, 10), "FocalLength": (670, 100), "LensModel": "Samsung S23 Main Camera", "Resolution": (4000, 3000)},
    # S22 시리즈
    {"Make": "Samsung", "Model": "SM-S908N", "Software": "S908NKSU3DWK1", "FNumber": (18, 10), "FocalLength": (630, 100), "LensModel": "Samsung S22 Ultra Wide Camera", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-S906N", "Software": "S906NKSU3CWK1", "FNumber": (18, 10), "FocalLength": (670, 100), "LensModel": "Samsung S22+ Main Camera", "Resolution": (4000, 3000)},
    # A 시리즈 (보급형 - 50MP = 4000x3000)
    {"Make": "Samsung", "Model": "SM-A556N", "Software": "A556NKSU1AWK1", "FNumber": (18, 10), "FocalLength": (550, 100), "LensModel": "Samsung A55 Main Camera", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-A546S", "Software": "A546SKSU2CWK1", "FNumber": (18, 10), "FocalLength": (550, 100), "LensModel": "Samsung A54 Main Camera", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-A346N", "Software": "A346NKSU2BWK1", "FNumber": (18, 10), "FocalLength": (550, 100), "LensModel": "Samsung A34 Main Camera", "Resolution": (4000, 3000)},
    # Z Fold/Flip 시리즈
    {"Make": "Samsung", "Model": "SM-F946N", "Software": "F946NKSU2BWK1", "FNumber": (18, 10), "FocalLength": (570, 100), "LensModel": "Samsung Z Fold5 Main Camera", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-F731N", "Software": "F731NKSU2BWK1", "FNumber": (18, 10), "FocalLength": (510, 100), "LensModel": "Samsung Z Flip5 Main Camera", "Resolution": (4000, 3000)},
    {"Make": "Samsung", "Model": "SM-F936N", "Software": "F936NKSU3CWK1", "FNumber": (18, 10), "FocalLength": (570, 100), "LensModel": "Samsung Z Fold4 Main Camera", "Resolution": (4000, 3000)},
    
    # === Apple iPhone (6개 = 30%) ===
    # iPhone 15 시리즈 (48MP = 4032x3024)
    {"Make": "Apple", "Model": "iPhone 15 Pro Max", "Software": "17.4.1", "FNumber": (18, 10), "FocalLength": (690, 100), "LensModel": "iPhone 15 Pro Max back triple camera 6.86mm f/1.78", "Resolution": (4032, 3024)},
    {"Make": "Apple", "Model": "iPhone 15 Pro", "Software": "17.4.1", "FNumber": (18, 10), "FocalLength": (690, 100), "LensModel": "iPhone 15 Pro back triple camera 6.86mm f/1.78", "Resolution": (4032, 3024)},
    {"Make": "Apple", "Model": "iPhone 15", "Software": "17.4.1", "FNumber": (16, 10), "FocalLength": (650, 100), "LensModel": "iPhone 15 back dual camera 6.5mm f/1.6", "Resolution": (4032, 3024)},
    # iPhone 14 시리즈
    {"Make": "Apple", "Model": "iPhone 14 Pro Max", "Software": "17.3.1", "FNumber": (18, 10), "FocalLength": (686, 100), "LensModel": "iPhone 14 Pro Max back triple camera 6.86mm f/1.78", "Resolution": (4032, 3024)},
    {"Make": "Apple", "Model": "iPhone 14 Pro", "Software": "17.3.1", "FNumber": (18, 10), "FocalLength": (686, 100), "LensModel": "iPhone 14 Pro back triple camera 6.86mm f/1.78", "Resolution": (4032, 3024)},
    # iPhone 13 시리즈
    {"Make": "Apple", "Model": "iPhone 13 Pro Max", "Software": "17.2", "FNumber": (15, 10), "FocalLength": (577, 100), "LensModel": "iPhone 13 Pro Max back triple camera 5.7mm f/1.5", "Resolution": (4032, 3024)},
]

class ImageProcessor:
    def __init__(self):
        pass

    def extract_coords_from_url(self, url: str) -> Optional[Tuple[float, float]]:
        """
        Extracts latitude and longitude from a Google Maps URL or raw "lat, lon" string.
        """
        try:
            url = url.strip()
            # Raw "lat, lon"
            raw_match = re.match(r'^(-?\d+\.\d+),\s*(-?\d+\.\d+)$', url)
            if raw_match: return float(raw_match.group(1)), float(raw_match.group(2))
            
            if "goo.gl" in url or "maps.app.goo.gl" in url:
                response = requests.get(url, allow_redirects=True)
                url = response.url

            match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
            if match: return float(match.group(1)), float(match.group(2))
            
            match_q = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', url)
            if match_q: return float(match_q.group(1)), float(match_q.group(2))
            return None
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return None

    def _to_dms_str(self, lat: float, lon: float) -> str:
        """
        Converts decimal coordinates to string format: 16°03'56.8"N 108°13'47.9"E
        """
        def format_coord(value, is_lat):
            direction = 'N' if value >= 0 else 'S'
            if not is_lat: direction = 'E' if value >= 0 else 'W'
            value = abs(value)
            deg = int(value)
            min_val = (value - deg) * 60
            min_int = int(min_val)
            sec_val = (min_val - min_int) * 60
            return f'{deg}°{min_int:02d}\'{sec_val:.1f}"{direction}'
        return f"{format_coord(lat, True)} {format_coord(lon, False)}"

    # === Enhancements ===
    def get_random_serial(self, length=12):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def get_random_datetime(self):
        """Returns (exif_format_string, datetime_object) for consistency."""
        days_ago = random.randint(1, 30)
        random_hour = random.randint(9, 22)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        target_date = datetime.now() - timedelta(days=days_ago)
        target_date = target_date.replace(hour=random_hour, minute=random_minute, second=random_second, microsecond=0)
        exif_str = target_date.strftime("%Y:%m:%d %H:%M:%S")
        return exif_str, target_date
    
    def generate_korean_filename(self, dt: datetime, device_make: str) -> str:
        """
        Generate Korean-market style filenames:
        - Samsung: YYYYMMDD_HHMMSS.jpg (matches DateTimeOriginal exactly)
        - Apple: IMG_XXXX.jpg (random 4 digits)
        Filename MUST match the device make - no mixing allowed!
        """
        if device_make.lower() == "samsung":
            # Samsung Galaxy style: YYYYMMDD_HHMMSS.jpg
            return dt.strftime("%Y%m%d_%H%M%S") + ".jpg"
        else:
            # Apple iPhone style: IMG_XXXX.jpg
            random_num = random.randint(1000, 9999)
            return f"IMG_{random_num}.jpg"

    def to_deg(self, value, loc):
        """
        Convert decimal degrees to DMS (Degrees, Minutes, Seconds) Rational format.
        삼성 갤러리 호환 형식: 분모 1000000 사용 (삼성 실제 사진과 동일)

        Returns: ((deg, 1), (min, 1), (sec*1000000, 1000000), 'N'/'S'/'E'/'W')
        """
        # Ref 결정: 위도는 N/S, 경도는 E/W
        if value < 0:
            loc_value = loc[0]  # 음수면 S 또는 W
        else:
            loc_value = loc[1]  # 양수 또는 0이면 N 또는 E

        abs_value = abs(value)
        deg = int(abs_value)
        t1 = (abs_value - deg) * 60
        min_val = int(t1)
        # 삼성 호환: 분모 1000000 사용 (실제 삼성 사진과 동일한 형식)
        sec_val = round((t1 - min_val) * 60 * 1000000)

        return (deg, 1), (min_val, 1), (sec_val, 1000000), loc_value

    def _convert_exif_to_little_endian(self, exif_bytes: bytes) -> bytes:
        """
        EXIF의 Byte Order를 Big Endian(MM)에서 Little Endian(II)으로 완전 변환.
        삼성 카메라는 Little Endian을 사용함.
        카카오톡/구글드라이브 등 일부 앱이 Big Endian EXIF를 제거하는 문제 해결.

        TIFF 구조 전체를 파싱하여 모든 multi-byte 값을 바이트 스왑함.
        """
        import struct

        if len(exif_bytes) < 14:
            return exif_bytes

        # EXIF 시작 위치 찾기 (Exif\x00\x00 다음)
        exif_header = b'Exif\x00\x00'
        idx = exif_bytes.find(exif_header)
        if idx == -1:
            return exif_bytes

        tiff_start = idx + 6  # TIFF 헤더 시작

        # 현재 byte order 확인
        if exif_bytes[tiff_start:tiff_start+2] != b'MM':
            # 이미 Little Endian이면 그대로 반환
            return exif_bytes

        # TIFF 데이터만 추출 (Exif\x00\x00 이후 전체)
        tiff_data = bytearray(exif_bytes[tiff_start:])
        tiff_len = len(tiff_data)

        def swap16(data, offset):
            """2바이트 Big->Little Endian 스왑"""
            if offset + 2 <= len(data):
                data[offset], data[offset+1] = data[offset+1], data[offset]

        def swap32(data, offset):
            """4바이트 Big->Little Endian 스왑"""
            if offset + 4 <= len(data):
                data[offset], data[offset+1], data[offset+2], data[offset+3] = \
                    data[offset+3], data[offset+2], data[offset+1], data[offset]

        def read_u16_be(data, offset):
            """Big Endian으로 2바이트 읽기"""
            if offset + 2 <= len(data):
                return (data[offset] << 8) | data[offset+1]
            return 0

        def read_u32_be(data, offset):
            """Big Endian으로 4바이트 읽기"""
            if offset + 4 <= len(data):
                return (data[offset] << 24) | (data[offset+1] << 16) | (data[offset+2] << 8) | data[offset+3]
            return 0

        # EXIF 타입별 바이트 크기
        type_sizes = {
            1: 1,   # BYTE
            2: 1,   # ASCII
            3: 2,   # SHORT (2 bytes)
            4: 4,   # LONG (4 bytes)
            5: 8,   # RATIONAL (2x4 bytes)
            6: 1,   # SBYTE
            7: 1,   # UNDEFINED
            8: 2,   # SSHORT
            9: 4,   # SLONG
            10: 8,  # SRATIONAL
            11: 4,  # FLOAT
            12: 8,  # DOUBLE
        }

        def swap_ifd_value(data, offset, value_type, count):
            """IFD 값/오프셋 필드 스왑 (4바이트)"""
            total_size = type_sizes.get(value_type, 1) * count

            if total_size <= 4:
                # 값이 4바이트 이하면 직접 저장됨
                if value_type in [3, 8]:  # SHORT, SSHORT (2 bytes each)
                    if count == 1:
                        swap16(data, offset)  # 첫 2바이트만 스왑
                    elif count == 2:
                        swap16(data, offset)
                        swap16(data, offset + 2)
                elif value_type in [4, 9, 11]:  # LONG, SLONG, FLOAT (4 bytes)
                    swap32(data, offset)
                # BYTE, ASCII, UNDEFINED는 스왑 불필요
            else:
                # 오프셋으로 저장됨 - 오프셋 자체를 스왑
                swap32(data, offset)

        def swap_external_values(data, offset, value_type, count, tag=0):
            """외부 데이터 영역의 값들 스왑"""
            if offset >= len(data):
                print(f"[SWAP] offset {offset} >= len(data) {len(data)}, skipping")
                return

            if value_type in [3, 8]:  # SHORT, SSHORT
                for i in range(count):
                    pos = offset + i * 2
                    if pos + 2 <= len(data):
                        swap16(data, pos)
            elif value_type in [4, 9, 11]:  # LONG, SLONG, FLOAT
                for i in range(count):
                    pos = offset + i * 4
                    if pos + 4 <= len(data):
                        swap32(data, pos)
            elif value_type in [5, 10, 12]:  # RATIONAL, SRATIONAL, DOUBLE
                for i in range(count):
                    pos = offset + i * 8
                    if pos + 8 <= len(data):
                        before_num = read_u32_be(data, pos)
                        before_den = read_u32_be(data, pos + 4)
                        swap32(data, pos)      # 분자
                        swap32(data, pos + 4)  # 분모
                        # 디버그: GPS 태그 (0x0002=Lat, 0x0004=Lon)
                        if tag in [0x0002, 0x0004]:
                            after = (data[pos], data[pos+1], data[pos+2], data[pos+3])
                            print(f"[SWAP RATIONAL] tag=0x{tag:04x} i={i} offset={pos}: {before_num}/{before_den} -> bytes={after}")

        def process_ifd(data, ifd_offset, processed_ifds=None):
            """IFD 처리 및 스왑"""
            if processed_ifds is None:
                processed_ifds = set()

            if ifd_offset in processed_ifds or ifd_offset < 8 or ifd_offset >= len(data) - 2:
                return
            processed_ifds.add(ifd_offset)

            # 엔트리 개수 읽기 (아직 Big Endian)
            num_entries = read_u16_be(data, ifd_offset)
            swap16(data, ifd_offset)  # 엔트리 개수 스왑

            if num_entries > 200 or num_entries == 0:  # 비정상적인 값 체크
                return

            # 각 엔트리 처리 (12바이트씩)
            for i in range(num_entries):
                entry_offset = ifd_offset + 2 + (i * 12)
                if entry_offset + 12 > len(data):
                    break

                # 태그, 타입, 카운트, 값/오프셋 읽기 (Big Endian)
                tag = read_u16_be(data, entry_offset)
                value_type = read_u16_be(data, entry_offset + 2)
                count = read_u32_be(data, entry_offset + 4)
                value_offset = read_u32_be(data, entry_offset + 8)

                # 엔트리 헤더 스왑
                swap16(data, entry_offset)      # 태그
                swap16(data, entry_offset + 2)  # 타입
                swap32(data, entry_offset + 4)  # 카운트

                # 값/오프셋 스왑
                total_size = type_sizes.get(value_type, 1) * count
                if total_size > 4:
                    # 외부 데이터 영역 스왑
                    swap_external_values(data, value_offset, value_type, count, tag)

                swap_ifd_value(data, entry_offset + 8, value_type, count)

                # 서브 IFD 처리 (ExifIFD, GPSIFD, InteropIFD)
                if tag in [0x8769, 0x8825, 0xA005] and total_size == 4:  # ExifIFDPointer, GPSInfoIFDPointer, InteroperabilityIFDPointer
                    sub_ifd_offset = value_offset
                    if sub_ifd_offset > 0 and sub_ifd_offset < len(data):
                        process_ifd(data, sub_ifd_offset, processed_ifds)

            # 다음 IFD 오프셋
            next_ifd_pos = ifd_offset + 2 + (num_entries * 12)
            if next_ifd_pos + 4 <= len(data):
                next_ifd_offset = read_u32_be(data, next_ifd_pos)
                swap32(data, next_ifd_pos)
                if next_ifd_offset > 0 and next_ifd_offset < len(data):
                    process_ifd(data, next_ifd_offset, processed_ifds)

        try:
            # TIFF 헤더 스왑
            tiff_data[0:2] = b'II'  # Byte order: Little Endian
            swap16(tiff_data, 2)    # Magic number: 0x002A -> 0x2A00

            # IFD0 오프셋 읽고 스왑
            ifd0_offset = read_u32_be(tiff_data, 4)
            swap32(tiff_data, 4)

            # 모든 IFD 처리
            if ifd0_offset > 0 and ifd0_offset < tiff_len:
                process_ifd(tiff_data, ifd0_offset)

            print(f"[BYTE ORDER] Big Endian(MM) -> Little Endian(II) 변환 완료")

            # 원본 구조 유지하면서 TIFF 부분만 교체
            result = bytearray(exif_bytes[:tiff_start])
            result.extend(tiff_data)
            return bytes(result)

        except Exception as e:
            print(f"[BYTE ORDER 오류] {e} - 원본 유지")
            return exif_bytes

    def _remove_jfif_segment(self, jpeg_data: bytes) -> bytes:
        """
        JPEG에서 JFIF(APP0) 세그먼트만 제거하고 나머지는 유지.
        삼성 갤러리 호환을 위해 FFD8 바로 다음에 EXIF(APP1)가 오도록 함.
        """
        if len(jpeg_data) < 4 or jpeg_data[0:2] != b'\xff\xd8':
            return jpeg_data

        result = bytearray(b'\xff\xd8')  # SOI 유지
        i = 2

        while i < len(jpeg_data) - 1:
            if jpeg_data[i] != 0xFF:
                i += 1
                continue

            marker = jpeg_data[i + 1]

            # APP0 (JFIF) - 스킵
            if marker == 0xE0:
                if i + 3 < len(jpeg_data):
                    length = (jpeg_data[i + 2] << 8) + jpeg_data[i + 3]
                    i += 2 + length
                else:
                    i += 2
                continue

            # APP1 (EXIF), APP2, DQT, SOF, DHT, SOS 등 - 나머지 전부 유지
            if marker in [0xE1, 0xE2, 0xDB, 0xC0, 0xC2, 0xC4, 0xDA, 0xDD, 0xFE]:
                # 이 마커부터 끝까지 전부 복사
                result.extend(jpeg_data[i:])
                break

            i += 1

        return bytes(result)

    def smart_upscale(self, img, min_size=4032):
        """
        Ultra High-Quality Upscale Pipeline:
        1. Resizing to 12MP Standard (4032x3024) - iPhone/Samsung Default
        2. LANCZOS resampling (highest quality)
        3. Detail enhancement filter
        4. UnsharpMask filter (sharpening)
        5. Contrast boost
        """
        w, h = img.size
        short_side = min(w, h)
        
        # Always upscale to at least 12MP short side standard (typically 3024px)
        # But here min_size is set to 4032 (Long side standard)
        # Let's ensure at least 3024px on short side
        target_short = 3024
        
        if short_side < target_short:
            ratio = target_short / short_side
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 1. Enhance Details first
        img = img.filter(ImageFilter.DETAIL)

        # 2. Apply UnsharpMask for crisp edges (Radius 2, Strength 120%)
        # Too much strength = fake. 120% is balanced for 12MP.
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))
        
        # 3. Slight Contrast Boost (Pop)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)  
        
        # 4. Final Sharpness Polish
        sharpener = ImageEnhance.Sharpness(img)
        img = sharpener.enhance(1.1) 
        
        return img

    def random_crop(self, img):
        """Random 1-5% crop"""
        width, height = img.size
        # Safety check for very small images
        if width < 100 or height < 100: return img
        
        crop_ratio = random.uniform(0.01, 0.05)
        crop_w = int(width * crop_ratio)
        crop_h = int(height * crop_ratio)
        
        left = random.randint(0, crop_w)
        top = random.randint(0, crop_h)
        right = width - (crop_w - left)
        bottom = height - (crop_h - top)
        return img.crop((left, top, right, bottom))

    def get_elevation(self, lat: float, lon: float) -> float:
        """
        Fetch real elevation from Open-Elevation API.
        Returns altitude in meters (float).
        Falls back to realistic Da Nang coastal value (3-6m) if API fails.
        """
        try:
            # Open-Elevation API (Free, no key required)
            url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
            response = requests.get(url, timeout=2) # Short timeout to avoid blocking
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    elevation = float(data['results'][0]['elevation'])
                    # Sanity check: If API returns unrealistically high value for city center (e.g. error), 
                    # basic outlier check or just accept it. 
                    # However, strictly for this user report, if it's > 200m in typical city, it might be hill.
                    # Let's trust API but print it.
                    print(f"[ELEVATION] Fetched real altitude: {elevation}m for {lat}, {lon}")
                    return elevation
        except Exception as e:
            print(f"[ELEVATION] API failed, using fallback: {e}")
        
        # Fallback: Realistic Da Nang riverfront/coastal low-lands (3m - 6m)
        return random.uniform(3.0, 6.0)

    def process_image(self, file_content: bytes, lat: float, lon: float, address_text="") -> Tuple[bytes, Dict]:
        """
        Processes image:
        1. Strip Metadata (메타데이터 완전 제거)
        2. PRNU Bypass (센서 지문 세탁 - 미세 노이즈)
        3. 메타데이터 강제 덮어쓰기

        [핵심] 픽셀 무손실 - 업스케일/크롭/필터 없음
        """
        import numpy as np

        print(f"\n{'='*60}")
        print(f"[처리 시작] 입력 크기: {len(file_content):,} bytes")
        print(f"[좌표] Lat: {lat}, Lon: {lon}")
        print(f"[주소] {address_text[:50] if address_text else '없음'}")

        try:
            img = Image.open(BytesIO(file_content))
            print(f"[이미지] {img.size[0]}x{img.size[1]}, {img.mode}, {img.format}")
        except Exception as e:
            print(f"[오류] 이미지 열기 실패: {e}")
            raise

        # Determine format (default JPEG if generic)
        original_format = img.format if img.format else 'JPEG'

        # 1. Strip Metadata (메타데이터 제거하면서 픽셀 보존)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        img_no_exif = Image.new(img.mode, img.size)
        img_no_exif.putdata(list(img.getdata()))

        # [픽셀 무손실] 업스케일, 크롭, 필터 없음

        # 2. PRNU Bypass - 센서 지문 세탁
        # 모든 픽셀에 ±1~2 미세 노이즈 추가 (육안 식별 불가)
        # numpy로 빠르게 처리
        img_array = np.array(img_no_exif, dtype=np.int16)
        noise = np.random.randint(-2, 3, img_array.shape, dtype=np.int16)  # -2 ~ +2
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        img_no_exif = Image.fromarray(img_array)

        width, height = img_no_exif.size
        print(f"[PRNU] 센서 지문 세탁 완료 (±2 노이즈, {width}x{height})")

        # 5. Smart GPS Fuzzing (Metropolitan Jitter)
        # Jitter within ~20m radius (0.0002 deg)
        lat_jitter = random.uniform(-0.0001, 0.0001)
        lon_jitter = random.uniform(-0.0001, 0.0001)
        
        jitter_lat = lat + lat_jitter
        jitter_lon = lon + lon_jitter
        
        # Get Real Elevation & Apply Floor Correction
        # Base elevation from API
        base_altitude = self.get_elevation(jitter_lat, jitter_lon)
        # Floor correction: Assume holding phone at standing height (approx 1.2m - 1.6m)
        # Optional: Add small random variance for holding height
        holding_height = random.uniform(1.2, 1.6)
        final_altitude = base_altitude + holding_height
        
        print(f"[GPS] Base Elev: {base_altitude:.2f}m + Hold: {holding_height:.2f}m = Final: {final_altitude:.2f}m")

        # Convert to DMS (Degrees, Minutes, Seconds) Rational format for EXIF
        lat_deg = self.to_deg(jitter_lat, ["S", "N"])
        lon_deg = self.to_deg(jitter_lon, ["W", "E"])

        # GPS 표준화 디버그 로그
        print(f"[GPS 표준화] 위도: {jitter_lat:.6f} -> DMS: {lat_deg[0][0]}°{lat_deg[1][0]}'{lat_deg[2][0]/10000:.4f}\" {lat_deg[3]}")
        print(f"[GPS 표준화] 경도: {jitter_lon:.6f} -> DMS: {lon_deg[0][0]}°{lon_deg[1][0]}'{lon_deg[2][0]/10000:.4f}\" {lon_deg[3]}")
        print(f"[GPS 표준화] 고도: {final_altitude:.2f}m -> Rational: ({int(final_altitude * 100)}, 100)")
        
        # 6. Generate Random Time
        # Within last 1 year, random time of day (distrubuted)
        # Or provided time if we want to be specific, but requirement says "Normalize"
        # Let's use a "Recent but random" approach: Past 1-30 days
        
        # 6. Device Selection & EXIF
        selected_device = random.choice(DEVICE_POOL)
        
        shot_time, shot_datetime = self.get_random_datetime()
        generated_filename = self.generate_korean_filename(shot_datetime, selected_device["Make"])
        # ISO 범위 제한: 50~800 (한국 실전용 - 너무 높은 ISO는 화질 의심받음)
        iso_val = random.choice([50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800])
        shutter_val = random.choice([(1, 2000), (1, 1000), (1, 500), (1, 250), (1, 125), (1, 60), (1, 30), (1, 15)])
        
        # Orientation Detection: 가로/세로 분석
        current_width, current_height = img_no_exif.size
        is_landscape = current_width >= current_height
        
        # EXIF Orientation value:
        # 1 = Horizontal (normal) - 가로 정방향
        # 6 = Rotate 90 CW - 세로 (폰 오른쪽으로 돌린 상태)
        # 8 = Rotate 270 CW - 세로 (폰 왼쪽으로 돌린 상태)
        if is_landscape:
            orientation_value = 1  # 가로 정방향
        else:
            orientation_value = random.choice([6, 8])  # 세로 (6 또는 8)

        # 최종 이미지 크기 (업스케일/크롭 후)
        final_width, final_height = img_no_exif.size

        # Zeroth IFD (TIFF) - 기기 정보 (디바이스별 분기)
        is_apple = selected_device["Make"].lower() == "apple"
        is_samsung = selected_device["Make"].lower() == "samsung"

        if is_apple:
            # Apple: Make 대문자, HostComputer 포함
            zeroth_ifd = {
                piexif.ImageIFD.Make: "Apple",
                piexif.ImageIFD.Model: selected_device["Model"],
                piexif.ImageIFD.Software: selected_device["Software"],
                piexif.ImageIFD.DateTime: shot_time,
                piexif.ImageIFD.Orientation: orientation_value,
                piexif.ImageIFD.XResolution: (72, 1),
                piexif.ImageIFD.YResolution: (72, 1),
                piexif.ImageIFD.ResolutionUnit: 2,
                piexif.ImageIFD.YCbCrPositioning: 1,
                piexif.ImageIFD.HostComputer: selected_device["Model"],
            }
        else:
            # Samsung: Make 소문자 "samsung", HostComputer 없음
            zeroth_ifd = {
                piexif.ImageIFD.Make: "samsung",
                piexif.ImageIFD.Model: selected_device["Model"],
                piexif.ImageIFD.Software: selected_device["Software"],
                piexif.ImageIFD.DateTime: shot_time,
                piexif.ImageIFD.Orientation: orientation_value,
                piexif.ImageIFD.XResolution: (72, 1),
                piexif.ImageIFD.YResolution: (72, 1),
                piexif.ImageIFD.ResolutionUnit: 2,
                piexif.ImageIFD.YCbCrPositioning: 1,
            }
        
        # 물리적 관계 계산
        import math
        fnumber_float = selected_device["FNumber"][0] / selected_device["FNumber"][1]
        aperture_value = 2 * math.log2(fnumber_float)
        aperture_rational = (int(aperture_value * 1000), 1000)

        exposure_float = shutter_val[0] / shutter_val[1]
        shutter_speed_value = -math.log2(exposure_float) if exposure_float > 0 else 0
        shutter_speed_rational = (int(shutter_speed_value * 10000), 10000)

        focal_mm = selected_device["FocalLength"][0] / selected_device["FocalLength"][1]

        # SubSecTime (밀리초 - 000~999 랜덤)
        subsec_time = str(random.randint(0, 999)).zfill(3)
        offset_time = "+09:00"

        if is_apple:
            # ============================================================
            # Apple iPhone 스타일 EXIF
            # ============================================================
            brightness_value = round(random.uniform(0.5, 3.0), 3)
            focal_35mm = 26  # iPhone 표준

            subject_x = final_width // 2 + random.randint(-200, 200)
            subject_y = final_height // 2 + random.randint(-200, 200)
            subject_w = random.randint(150, 300)
            subject_h = random.randint(150, 300)

            lens_spec = (
                (425, 100), (600, 100),  # focal range
                selected_device["FNumber"], (24, 10),  # aperture range
            )

            exif_ifd = {
                piexif.ExifIFD.DateTimeOriginal: shot_time,
                piexif.ExifIFD.DateTimeDigitized: shot_time,
                piexif.ExifIFD.OffsetTime: offset_time,
                piexif.ExifIFD.OffsetTimeOriginal: offset_time,
                piexif.ExifIFD.OffsetTimeDigitized: offset_time,
                piexif.ExifIFD.SubSecTimeOriginal: subsec_time,
                piexif.ExifIFD.SubSecTimeDigitized: subsec_time,
                piexif.ExifIFD.PixelXDimension: final_width,
                piexif.ExifIFD.PixelYDimension: final_height,
                piexif.ExifIFD.ColorSpace: 65535,
                piexif.ExifIFD.ComponentsConfiguration: b'\x01\x02\x03\x00',
                piexif.ExifIFD.ExposureTime: shutter_val,
                piexif.ExifIFD.FNumber: selected_device["FNumber"],
                piexif.ExifIFD.ISOSpeedRatings: iso_val,
                piexif.ExifIFD.ExposureProgram: 2,
                piexif.ExifIFD.ExposureMode: 0,
                piexif.ExifIFD.ExposureBiasValue: (0, 1),
                piexif.ExifIFD.ApertureValue: aperture_rational,
                piexif.ExifIFD.ShutterSpeedValue: shutter_speed_rational,
                piexif.ExifIFD.BrightnessValue: (int(brightness_value * 1000), 1000),
                piexif.ExifIFD.FocalLength: selected_device["FocalLength"],
                piexif.ExifIFD.FocalLengthIn35mmFilm: focal_35mm,
                piexif.ExifIFD.LensMake: selected_device["Make"],
                piexif.ExifIFD.LensModel: selected_device["LensModel"],
                piexif.ExifIFD.LensSpecification: lens_spec,
                piexif.ExifIFD.MeteringMode: 5,  # Pattern
                piexif.ExifIFD.Flash: 16,
                piexif.ExifIFD.WhiteBalance: 0,
                piexif.ExifIFD.SceneCaptureType: 0,
                piexif.ExifIFD.SceneType: b'\x01',
                piexif.ExifIFD.SensingMethod: 2,
                piexif.ExifIFD.SubjectArea: (subject_x, subject_y, subject_w, subject_h),
                piexif.ExifIFD.ExifVersion: b'0232',
                piexif.ExifIFD.FlashpixVersion: b'0100',
                piexif.ExifIFD.DigitalZoomRatio: (1, 1),
            }
        else:
            # ============================================================
            # Samsung Galaxy 스타일 EXIF
            # ============================================================
            focal_35mm = 23  # 삼성 표준

            exif_ifd = {
                piexif.ExifIFD.DateTimeOriginal: shot_time,
                piexif.ExifIFD.DateTimeDigitized: shot_time,
                piexif.ExifIFD.OffsetTime: offset_time,
                piexif.ExifIFD.OffsetTimeOriginal: offset_time,
                piexif.ExifIFD.SubSecTime: subsec_time,
                piexif.ExifIFD.SubSecTimeOriginal: subsec_time,
                piexif.ExifIFD.SubSecTimeDigitized: subsec_time,
                piexif.ExifIFD.PixelXDimension: final_width,
                piexif.ExifIFD.PixelYDimension: final_height,
                piexif.ExifIFD.ColorSpace: 65535,
                piexif.ExifIFD.ExposureTime: shutter_val,
                piexif.ExifIFD.FNumber: selected_device["FNumber"],
                piexif.ExifIFD.ISOSpeedRatings: iso_val,
                piexif.ExifIFD.ExposureProgram: 2,
                piexif.ExifIFD.ExposureMode: 0,
                piexif.ExifIFD.ExposureBiasValue: (0, 1),
                piexif.ExifIFD.ApertureValue: aperture_rational,
                piexif.ExifIFD.MaxApertureValue: aperture_rational,  # 삼성 전용
                piexif.ExifIFD.ShutterSpeedValue: shutter_speed_rational,
                piexif.ExifIFD.FocalLength: selected_device["FocalLength"],
                piexif.ExifIFD.FocalLengthIn35mmFilm: focal_35mm,
                piexif.ExifIFD.MeteringMode: 2,  # CenterWeightedAverage
                piexif.ExifIFD.Flash: 0,  # No flash
                piexif.ExifIFD.WhiteBalance: 0,
                piexif.ExifIFD.SceneCaptureType: 0,
                piexif.ExifIFD.ExifVersion: b'0220',  # EXIF 2.2
                piexif.ExifIFD.FlashpixVersion: b'0100',
                piexif.ExifIFD.DigitalZoomRatio: (1, 1),
            }
        
        # ============================================================
        # GPS IFD - 디바이스별 분리 (Apple vs Samsung)
        # ============================================================
        # Apple iPhone: 15개 GPS 태그 (시간, 속도, 방향, 오차 등 포함)
        # Samsung Galaxy: 3개 GPS 태그만 (위도, 경도, 고도)
        # ============================================================

        if is_apple:
            # ============================================================
            # Apple iPhone GPS IFD - 15개 태그 전체
            # ============================================================
            # GPS 시간 정보 생성 (UTC 기준 - 한국시간에서 9시간 빼기)
            utc_hour = (shot_datetime.hour - 9) % 24
            gps_timestamp = (
                (utc_hour, 1),
                (shot_datetime.minute, 1),
                (shot_datetime.second, 1)
            )
            gps_datestamp = shot_datetime.strftime("%Y:%m:%d")

            # GPS 방향 (나침반 - 0~359도)
            img_direction = round(random.uniform(0, 359.999), 3)
            dest_bearing = round(random.uniform(0, 359.999), 3)

            # GPS 수평 오차 (5~25m 정도가 일반적)
            h_positioning_error = round(random.uniform(5, 25), 3)

            gps_ifd = {
                # 위도/경도
                piexif.GPSIFD.GPSLatitudeRef: lat_deg[3].encode('ascii'),
                piexif.GPSIFD.GPSLatitude: (lat_deg[0], lat_deg[1], lat_deg[2]),
                piexif.GPSIFD.GPSLongitudeRef: lon_deg[3].encode('ascii'),
                piexif.GPSIFD.GPSLongitude: (lon_deg[0], lon_deg[1], lon_deg[2]),

                # 고도
                piexif.GPSIFD.GPSAltitudeRef: 0,  # 해발
                piexif.GPSIFD.GPSAltitude: (int(final_altitude * 100), 100),

                # 시간 (UTC)
                piexif.GPSIFD.GPSTimeStamp: gps_timestamp,
                piexif.GPSIFD.GPSDateStamp: gps_datestamp.encode('ascii'),

                # 속도
                piexif.GPSIFD.GPSSpeedRef: b'K',  # km/h
                piexif.GPSIFD.GPSSpeed: (0, 1),   # 정지 상태

                # 이미지 방향 (카메라가 향한 방향)
                piexif.GPSIFD.GPSImgDirectionRef: b'T',  # True north (진북)
                piexif.GPSIFD.GPSImgDirection: (int(img_direction * 1000), 1000),

                # 대상 방위 (목적지 방향)
                piexif.GPSIFD.GPSDestBearingRef: b'T',  # True north
                piexif.GPSIFD.GPSDestBearing: (int(dest_bearing * 1000), 1000),

                # 수평 위치 오차 (GPS 정확도)
                piexif.GPSIFD.GPSHPositioningError: (int(h_positioning_error * 1000), 1000),
            }
        else:
            # ============================================================
            # Samsung Galaxy GPS IFD - 3개 태그만 (실제 삼성 사진과 동일)
            # ============================================================
            # 고도, 위도, 경도만 저장 (GPSTimeStamp, GPSSpeed 등 없음)
            # ============================================================
            gps_ifd = {
                # 위도
                piexif.GPSIFD.GPSLatitudeRef: lat_deg[3].encode('ascii'),
                piexif.GPSIFD.GPSLatitude: (lat_deg[0], lat_deg[1], lat_deg[2]),

                # 경도
                piexif.GPSIFD.GPSLongitudeRef: lon_deg[3].encode('ascii'),
                piexif.GPSIFD.GPSLongitude: (lon_deg[0], lon_deg[1], lon_deg[2]),

                # 고도
                piexif.GPSIFD.GPSAltitudeRef: 0,  # 해발
                piexif.GPSIFD.GPSAltitude: (int(final_altitude * 100), 100),
            }

        # ============================================================
        # 썸네일 생성 - 삼성 갤러리 인덱싱 필수!
        # ============================================================
        # 삼성 갤러리는 썸네일이 있어야 GPS 메타데이터를 제대로 표시함
        # 표준 썸네일 크기: 160x120 (EXIF 표준) 또는 비율 유지 최대 160px
        # ============================================================

        # 썸네일 생성 (512px 기준 - 삼성 실제 사진과 동일)
        thumb_max_size = 512
        thumb_img = img_no_exif.copy()
        thumb_img.thumbnail((thumb_max_size, thumb_max_size), Image.Resampling.LANCZOS)

        # 썸네일을 JPEG 바이트로 변환
        thumb_buffer = BytesIO()
        thumb_img.save(thumb_buffer, format='JPEG', quality=75)
        thumbnail_bytes = thumb_buffer.getvalue()

        thumb_w, thumb_h = thumb_img.size
        print(f"[썸네일] 생성 완료: {thumb_w}x{thumb_h}, {len(thumbnail_bytes)} bytes")

        # 1st IFD (썸네일 IFD) - 삼성 갤러리 필수 태그
        first_ifd = {
            piexif.ImageIFD.ImageWidth: thumb_w,
            piexif.ImageIFD.ImageLength: thumb_h,
            piexif.ImageIFD.Compression: 6,  # 6 = JPEG compression
            piexif.ImageIFD.Orientation: orientation_value,
            piexif.ImageIFD.XResolution: (72, 1),
            piexif.ImageIFD.YResolution: (72, 1),
            piexif.ImageIFD.ResolutionUnit: 2,
            piexif.ImageIFD.YCbCrPositioning: 1,
            # JPEGInterchangeFormat과 JPEGInterchangeFormatLength는 piexif가 자동 설정
        }

        # ============================================================
        # EXIF Dictionary 조립 - MakerNote 없이 깨끗한 표준 데이터만
        # ============================================================

        exif_dict = {
            "0th": zeroth_ifd,      # 기본 IFD
            "Exif": exif_ifd,       # EXIF IFD
            "GPS": gps_ifd,         # GPS IFD (표준 규격)
            "1st": first_ifd,       # 썸네일 IFD (삼성 갤러리 필수!)
            "Interop": {},          # 상호운용성 IFD
            "thumbnail": thumbnail_bytes,  # 썸네일 JPEG 데이터
        }

        try:
            exif_bytes = piexif.dump(exif_dict)
            device_type = "iPhone" if is_apple else "Samsung"
            print(f"[EXIF] 덤프 완료: {len(exif_bytes)} bytes ({device_type} 스타일, GPS 태그 {len(gps_ifd)}개)")
        except Exception as e:
            print(f"[EXIF 오류] {e}")
            raise

        output_stream = BytesIO()

        try:
            # JPEG 저장 (EXIF 포함) - Big Endian(MM) 그대로 사용
            img_no_exif.save(output_stream, format="JPEG", exif=exif_bytes, quality=100, subsampling=0)
            output_data = output_stream.getvalue()

            # JFIF 세그먼트 제거 (카메라 사진에는 JFIF 없음)
            output_data = self._remove_jfif_segment(output_data)
            print(f"[저장] {len(output_data)} bytes (JFIF 제거됨)")

        except Exception as e:
            raise
        
        # Prepare Metadata Info for UI
        metadata_info = {
            "make": selected_device["Make"],
            "model": selected_device["Model"],
            "software": selected_device["Software"],
            "datetime": shot_time,
            "formatted_coords": self._to_dms_str(jitter_lat, jitter_lon),
            "gps": {
                "lat": jitter_lat,
                "lon": jitter_lon,
                "altitude": round(final_altitude, 2),
                "altitude_ref": "Above Sea Level"
            },
            "gps_version": "2.2.0.0",
            "generated_filename": generated_filename
        }

        print(f"[완료] GPS IFD 표준 규격 적용 완료 - GPSVersionID: 2.2.0.0")
        
        return output_data, metadata_info

    def process_zip(self, zip_content: bytes, lat: float, lon: float, address_text="") -> bytes:
        """
        Processes a ZIP file containing images.
        Returns a new ZIP file (bytes) with normalized images.
        Filenames are generated using Korean-style naming (Samsung/iPhone).
        """
        input_zip = zipfile.ZipFile(BytesIO(zip_content))
        output_buffer = BytesIO()
        output_zip = zipfile.ZipFile(output_buffer, 'w', zipfile.ZIP_DEFLATED)
        
        for filename in input_zip.namelist():
            # Skip directories or non-images (simple check)
            if filename.startswith('__MACOSX') or filename.startswith('.'):
                continue
                
            lowercase_name = filename.lower()
            if not (lowercase_name.endswith('.jpg') or lowercase_name.endswith('.jpeg') or lowercase_name.endswith('.png')):
                continue
                
            try:
                file_data = input_zip.read(filename)
                # We reuse process_image logic - it returns Korean-style filename in metadata
                processed_bytes, metadata = self.process_image(file_data, lat, lon, address_text)
                # Use Korean-style generated filename instead of original
                new_filename = metadata.get("generated_filename", filename)
                output_zip.writestr(new_filename, processed_bytes)
            except Exception as e:
                print(f"Skipping {filename}: {e}")
                
        output_zip.close()
        return output_buffer.getvalue()

    def analyze_metadata(self, file_content: bytes, filename: str) -> Dict:
        """
        Analyzes an image and returns a comprehensive metadata summary.
        Categories: Identity, Location & Security, Camera Specs, Deep Metadata
        """
        import hashlib
        
        def safe_decode(val):
            """Safely decode bytes or return str as-is."""
            if val is None:
                return ""
            if isinstance(val, bytes):
                return val.decode('utf-8', errors='ignore').strip()
            if isinstance(val, str):
                return val.strip()
            return str(val)
        
        # Calculate file hash
        file_hash = hashlib.md5(file_content).hexdigest()
        
        try:
            img = Image.open(BytesIO(file_content))
            width, height = img.size
            resolution = f"{width} x {height}"
            
            exif_data = img.info.get("exif", b"")
            if not exif_data:
                # No EXIF data at all
                raise ValueError("No EXIF data")
            
            exif_dict = piexif.load(exif_data)
            
            # === 1. Identity ===
            make = safe_decode(exif_dict.get("0th", {}).get(piexif.ImageIFD.Make, b""))
            model = safe_decode(exif_dict.get("0th", {}).get(piexif.ImageIFD.Model, b""))
            datetime_original = safe_decode(exif_dict.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal, b""))
            
            # === 2. Location & Security ===
            gps_info = exif_dict.get("GPS", {})
            has_gps = bool(gps_info)
            gps_coords = "-"
            
            if has_gps:
                try:
                    lat_dms = gps_info.get(piexif.GPSIFD.GPSLatitude)
                    lat_ref_raw = gps_info.get(piexif.GPSIFD.GPSLatitudeRef, b'N')
                    lat_ref = safe_decode(lat_ref_raw) or 'N'
                    lon_dms = gps_info.get(piexif.GPSIFD.GPSLongitude)
                    lon_ref_raw = gps_info.get(piexif.GPSIFD.GPSLongitudeRef, b'E')
                    lon_ref = safe_decode(lon_ref_raw) or 'E'
                    
                    if lat_dms and lon_dms:
                        lat = lat_dms[0][0]/lat_dms[0][1] + lat_dms[1][0]/(lat_dms[1][1]*60) + lat_dms[2][0]/(lat_dms[2][1]*3600)
                        lon = lon_dms[0][0]/lon_dms[0][1] + lon_dms[1][0]/(lon_dms[1][1]*60) + lon_dms[2][0]/(lon_dms[2][1]*3600)
                        if lat_ref == 'S': lat = -lat
                        if lon_ref == 'W': lon = -lon
                        gps_coords = f"{lat:.6f}, {lon:.6f}"
                except Exception as e:
                    gps_coords = "파싱 오류"
            
            # === 3. Camera Specs ===
            # Aperture (FNumber)
            fnumber_raw = exif_dict.get("Exif", {}).get(piexif.ExifIFD.FNumber, None)
            if fnumber_raw and isinstance(fnumber_raw, tuple) and len(fnumber_raw) == 2:
                aperture = f"f/{fnumber_raw[0] / fnumber_raw[1]:.1f}"
            else:
                aperture = "-"
            
            # ISO
            iso_raw = exif_dict.get("Exif", {}).get(piexif.ExifIFD.ISOSpeedRatings, None)
            iso = str(iso_raw) if iso_raw else "-"
            
            # Focal Length
            focal_raw = exif_dict.get("Exif", {}).get(piexif.ExifIFD.FocalLength, None)
            if focal_raw and isinstance(focal_raw, tuple) and len(focal_raw) == 2:
                focal_length = f"{focal_raw[0] / focal_raw[1]:.2f}mm"
            else:
                focal_length = "-"
            
            # Shutter Speed (Exposure Time)
            shutter_raw = exif_dict.get("Exif", {}).get(piexif.ExifIFD.ExposureTime, None)
            if shutter_raw and isinstance(shutter_raw, tuple) and len(shutter_raw) == 2:
                shutter_speed = f"1/{int(shutter_raw[1] / shutter_raw[0])}" if shutter_raw[0] > 0 else "-"
            else:
                shutter_speed = "-"
            
            # Lens Model
            lens_model_raw = exif_dict.get("Exif", {}).get(piexif.ExifIFD.LensModel, b"")
            lens_model = safe_decode(lens_model_raw) or "-"
            
            # === 4. Deep Metadata ===
            # Software
            software = safe_decode(exif_dict.get("0th", {}).get(piexif.ImageIFD.Software, b""))
            
            # Device Serial (BodySerialNumber)
            body_serial_raw = exif_dict.get("Exif", {}).get(piexif.ExifIFD.BodySerialNumber, b"")
            body_serial = safe_decode(body_serial_raw) or "-"
            
            # Lens Serial
            lens_serial_raw = exif_dict.get("Exif", {}).get(piexif.ExifIFD.LensSerialNumber, b"")
            lens_serial = safe_decode(lens_serial_raw) or "-"
            
            # === 5. Address Tag (from ImageDescription) ===
            image_desc_raw = exif_dict.get("0th", {}).get(piexif.ImageIFD.ImageDescription, b"")
            address_tag = safe_decode(image_desc_raw) or "-"
            
            # Risk Level
            is_risky = has_gps or bool(make) or bool(model)
            
            return {
                # Identity
                "filename": filename,
                "model": model or "-",
                "make": make or "-",
                "datetime": datetime_original or "-",
                # Location & Security
                "gps_coords": gps_coords,
                "has_gps": has_gps,
                "file_hash": file_hash[:8],
                "resolution": resolution,
                # Camera Specs
                "aperture": aperture,
                "focal_length": focal_length,
                "iso": iso,
                "shutter_speed": shutter_speed,
                "lens_model": lens_model or "-",
                # Deep Metadata
                "body_serial": body_serial or "-",
                "lens_serial": lens_serial or "-",
                "software": software or "-",
                "address_tag": address_tag,
                # Status
                "is_risky": is_risky
            }
        except Exception as e:
            return {
                "filename": filename,
                "model": "-", "make": "-", "datetime": "-",
                "gps_coords": "-", "has_gps": False, "file_hash": file_hash[:8], "resolution": "-",
                "aperture": "-", "focal_length": "-", "iso": "-", "shutter_speed": "-", "lens_model": "-",
                "body_serial": "-", "lens_serial": "-", "software": "-", "address_tag": "-",
                "is_risky": False
            }

    def analyze_zip(self, zip_content: bytes) -> List[Dict]:
        """
        Analyzes all images in a ZIP file.
        """
        input_zip = zipfile.ZipFile(BytesIO(zip_content))
        results = []
        
        for filename in input_zip.namelist():
             if filename.startswith('__MACOSX') or filename.startswith('.'):
                continue
             if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
             
             try:
                 file_data = input_zip.read(filename)
                 result = self.analyze_metadata(file_data, filename)
                 results.append(result)
             except:
                 pass
        
        return results
