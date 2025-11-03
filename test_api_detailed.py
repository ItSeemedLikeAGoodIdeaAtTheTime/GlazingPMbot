#!/usr/bin/env python3
"""
Detailed API Test - Shows exact error
"""

import os
import sys

api_key = os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ API key not found")
    sys.exit(1)

print(f"API Key: {api_key[:20]}...{api_key[-4:]}")

try:
    from anthropic import Anthropic

    print("\nTesting connection...")
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'test successful'"}]
    )

    print(f"\n✅ SUCCESS: {response.content[0].text}")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Details: {str(e)}")

    # More diagnostics
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
