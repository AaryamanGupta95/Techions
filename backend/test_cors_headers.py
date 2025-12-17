"""Test script to verify CORS headers are being sent"""
import requests

# Test OPTIONS request (preflight)
print("Testing OPTIONS (preflight) request...")
response = requests.options(
    "http://localhost:8000/api/v1/vehicles/customer/CUST_001",
    headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization"
    }
)
print(f"Status: {response.status_code}")
print("CORS Headers:")
for header in response.headers:
    if "access-control" in header.lower():
        print(f"  {header}: {response.headers[header]}")

# Test GET request
print("\nTesting GET request...")
response = requests.get(
    "http://localhost:8000/api/v1/health",
    headers={"Origin": "http://localhost:3000"}
)
print(f"Status: {response.status_code}")
print("CORS Headers:")
for header in response.headers:
    if "access-control" in header.lower():
        print(f"  {header}: {response.headers[header]}")

