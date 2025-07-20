#!/usr/bin/env python3
"""
Syntax test for CI/CD
Tests that all modules can be imported without errors
"""

import sys


def test_imports():
    """Test that all modules can be imported"""
    try:
        # Test main module
        import main

        print("✅ main.py imports successfully")

        # Test cogs
        import cogs.general

        print("✅ cogs.general imports successfully")

        import cogs.fun

        print("✅ cogs.fun imports successfully")

        # Test utils
        import keep_alive

        print("✅ keep_alive.py imports successfully")

        print("\n✅ All modules import successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    if test_imports():
        sys.exit(0)
    else:
        sys.exit(1)
