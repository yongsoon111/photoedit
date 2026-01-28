import requests

def test_extract_location():
    url = "http://localhost:8000/extract-location"
    
    # Test case: Google Maps @ format
    maps_url = "https://www.google.com/maps/place/Seoul+City+Hall/@37.566535,126.9779692,17z/data=!3m1!4b1!4m6!3m5!1s0x357ca1b47 db84013:0x1c95353d2c803855!8m2!3d37.566535!4d126.9779692!16zL20vMDF3Nnc?entry=ttu"
    
    print(f"Testing URL: {maps_url}")
    try:
        response = requests.post(url, json={"url": maps_url})
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Lat: {data['lat']}, Lon: {data['lon']}")
            
            # Simple assertion (approximate)
            if 37.5 < data['lat'] < 37.6 and 126.9 < data['lon'] < 127.0:
                 print("Verification PASSED: Coordinates are within Seoul range.")
            else:
                 print("Verification FAILED: Coordinates out of expected range.")
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_extract_location()
