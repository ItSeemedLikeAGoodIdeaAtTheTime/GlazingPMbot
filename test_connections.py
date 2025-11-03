#!/usr/bin/env python3
"""
Quick Connection Test Script
Tests both Anthropic API and Google Sheets API
"""

import os
import sys

print("\n" + "="*70)
print("  CONNECTION TESTS - Anthropic API & Google Sheets")
print("="*70)

# Test 1: Anthropic API
print("\n[1/2] Testing Anthropic API...")
print("-" * 70)

api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("anthropicAPIkey")

if not api_key:
    print("FAIL: No API key found")
    print("Set: export ANTHROPIC_API_KEY=your-key-here")
    sys.exit(1)

try:
    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=50,
        messages=[{'role': 'user', 'content': 'Reply with: Connection test passed'}]
    )

    print(f"SUCCESS: {response.content[0].text}")
    print(f"Model: {response.model}")
    print(f"Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)

# Test 2: Google Sheets API
print("\n[2/2] Testing Google Sheets API...")
print("-" * 70)

try:
    from pathlib import Path
    import json

    creds_file = Path("credentials.json")
    if not creds_file.exists():
        print("FAIL: credentials.json not found")
        print("Download from Google Cloud Console")
        sys.exit(1)

    print("SUCCESS: credentials.json found")

    # Try importing Google APIs
    import gspread
    from google.oauth2.service_account import Credentials

    print("SUCCESS: Google API libraries installed")

    # Try authenticating
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    gc = gspread.authorize(creds)

    print("SUCCESS: Google Sheets authentication working")

except ImportError as e:
    print(f"FAIL: Missing library - {e}")
    print("Install: pip install gspread google-auth")
    sys.exit(1)

except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("  ALL CONNECTION TESTS PASSED!")
print("="*70)
print("\nYou're ready to:")
print("  - Process contracts with Claude AI")
print("  - Push SOVs to Google Sheets")
print("  - Create project tracking dashboards")
print("  - Manage vendor data in sheets")
print("\n" + "="*70 + "\n")
