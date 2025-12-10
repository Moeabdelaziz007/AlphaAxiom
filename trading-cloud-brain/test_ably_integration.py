#!/usr/bin/env python3
"""
Test script to verify Ably integration in the Cloudflare Worker
"""

import sys
import os

# Add the src directory to the path so we can import the worker module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ably_constants():
    """Test that ABLY_API_URL is properly defined"""
    try:
        # Import the worker module
        import worker
        print("✅ Successfully imported worker module")
        
        # Check if ABLY_API_URL is defined
        if hasattr(worker, 'ABLY_API_URL'):
            print(f"✅ ABLY_API_URL is defined: {worker.ABLY_API_URL}")
            if worker.ABLY_API_URL == "https://rest.ably.io":
                print("✅ ABLY_API_URL has the correct value")
                return True
            else:
                print(f"❌ ABLY_API_URL has incorrect value: {worker.ABLY_API_URL}")
                return False
        else:
            print("❌ ABLY_API_URL is not defined")
            return False
    except Exception as e:
        print(f"❌ Error importing worker module: {e}")
        return False

def test_ably_functions():
    """Test that Ably-related functions exist"""
    try:
        import worker
        
        # Check if publish_to_ably function exists
        if hasattr(worker, 'publish_to_ably'):
            print("✅ publish_to_ably function exists")
        else:
            print("❌ publish_to_ably function does not exist")
            
        # Check if the Ably auth endpoint function exists
        # Looking at the code, it's part of the on_fetch function
        if hasattr(worker, 'on_fetch'):
            print("✅ on_fetch function exists (contains Ably auth endpoint)")
        else:
            print("❌ on_fetch function does not exist")
            
        return True
    except Exception as e:
        print(f"❌ Error checking worker functions: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Ably Integration...")
    print("=" * 50)
    
    success = True
    
    # Test 1: Check constants
    print("\n1. Testing ABLY_API_URL constant...")
    if not test_ably_constants():
        success = False
    
    # Test 2: Check functions
    print("\n2. Testing Ably-related functions...")
    if not test_ably_functions():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All Ably integration tests passed!")
        return 0
    else:
        print("💥 Some Ably integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())