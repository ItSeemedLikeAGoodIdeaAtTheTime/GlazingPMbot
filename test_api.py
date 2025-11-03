#!/usr/bin/env python3
"""
Test Anthropic API Connection
Quick test to verify your API key is working
"""

import os
import sys

print("\n" + "="*60)
print("  ANTHROPIC API CONNECTION TEST")
print("="*60 + "\n")

# Check if API key is set
api_key = os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ ANTHROPIC_API_KEY not found in environment variables\n")
    print("To set your API key:\n")
    print("Windows (Command Prompt):")
    print('  set ANTHROPIC_API_KEY=sk-ant-...')
    print("\nWindows (PowerShell):")
    print('  $env:ANTHROPIC_API_KEY="sk-ant-..."')
    print("\nMac/Linux:")
    print('  export ANTHROPIC_API_KEY=sk-ant-...')
    print("\nOr create a .env file with:")
    print('  ANTHROPIC_API_KEY=sk-ant-...')
    print("\nGet your API key at: https://console.anthropic.com/")
    print("\n" + "="*60 + "\n")
    sys.exit(1)

print(f"✅ API Key found: {api_key[:15]}...{api_key[-4:]}")
print("\nTesting connection...\n")

try:
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)

    # Simple test message
    print("Sending test message to Claude API...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": "Reply with exactly: 'API connection successful!'"
        }]
    )

    reply = response.content[0].text

    print(f"\n✅ Claude responded: {reply}\n")
    print("="*60)
    print("  ✅ API CONNECTION SUCCESSFUL!")
    print("="*60)
    print(f"\nModel: {response.model}")
    print(f"Usage: {response.usage.input_tokens} input tokens, {response.usage.output_tokens} output tokens")
    print(f"\nYou're ready to process projects!")
    print("\n" + "="*60 + "\n")

except ImportError:
    print("❌ Anthropic library not installed\n")
    print("Install it with:")
    print("  pip install anthropic\n")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ API Error: {e}\n")
    print("Common issues:")
    print("  - Invalid API key (check for typos)")
    print("  - Network connection issues")
    print("  - Insufficient API credits")
    print("\nCheck your API key at: https://console.anthropic.com/")
    print("\n" + "="*60 + "\n")
    sys.exit(1)
