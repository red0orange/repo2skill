#!/usr/bin/env python3
"""Test Alibaba Bailian API connection."""

import asyncio
import aiohttp
import json

async def test_bailian_api():
    api_key = "sk-b40c3570edf64a3fbca9a9bc8863c014"
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, API test successful!' in JSON format: {\"message\": \"...\"}"}
        ],
        "temperature": 0.1
    }

    print("Testing Alibaba Bailian API...")
    print(f"URL: {api_url}")
    print(f"Model: qwen-plus")
    print()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"Status: {response.status}")

                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    print(f"✓ API test successful!")
                    print(f"Response: {content}")
                    return True
                else:
                    text = await response.text()
                    print(f"✗ API test failed")
                    print(f"Error: {text}")
                    return False

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bailian_api())
    exit(0 if success else 1)
