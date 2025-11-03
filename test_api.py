import requests
import json

BASE_URL = "https://fioletowe.live/api/v1"

print("Testing car-models API endpoint...")
print("=" * 60)

for model_type in [1, 2]:
    print(f"\nTesting modelType={model_type}")
    print("-" * 60)
    
    url = f"{BASE_URL}/car-models"
    params = {"modelType": model_type, "electric": False}
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"Keys in response: {list(data.keys())}")
                print(f"\nFirst 500 chars of response:")
                print(json.dumps(data, indent=2)[:500])
            elif isinstance(data, list):
                print(f"Response is a list with {len(data)} items")
                if data:
                    print(f"\nFirst item:")
                    print(json.dumps(data[0], indent=2))
            else:
                print(f"Unexpected type: {type(data)}")
        else:
            print(f"Error response:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Testing cars API endpoint...")
print("=" * 60)

try:
    response = requests.get(f"{BASE_URL}/cars", params={"zoneId": 1})
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Keys in response: {list(data.keys())}")
            if 'cars' in data:
                print(f"Number of cars: {len(data['cars'])}")
                if data['cars']:
                    print(f"\nFirst car:")
                    print(json.dumps(data['cars'][0], indent=2))
except Exception as e:
    print(f"Exception occurred: {e}")
    import traceback
    traceback.print_exc()
