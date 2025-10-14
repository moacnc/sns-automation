"""
Debug script to test tab clicking
"""
import sys
import time
from loguru import logger
from src.gramaddict_wrapper.navigation import InstagramNavigator

logger.remove()
logger.add(sys.stdout, level="DEBUG")

def main():
    print("=" * 60)
    print("Debug: Testing Direct Tab Click")
    print("=" * 60)

    # Initialize navigator
    nav = InstagramNavigator()

    print("\n[1] Connecting to device...")
    if not nav.connect():
        print("❌ Failed to connect")
        return

    print("✅ Connected\n")

    # Test search tab directly
    print("[2] Testing search_tab resource ID...")
    print(f"    Resource ID: com.instagram.android:id/search_tab")

    try:
        # Direct test
        print("\n[2.1] Trying device.find()...")
        tab = nav.device.find(
            resourceId="com.instagram.android:id/search_tab"
        )

        print(f"[2.2] Checking if exists()...")
        start = time.time()
        exists = tab.exists()
        elapsed = time.time() - start

        print(f"    Result: {exists}")
        print(f"    Time taken: {elapsed:.2f}s")

        if exists:
            print("\n[2.3] Element found! Getting info...")
            try:
                info = tab.info
                print(f"    Info: {info}")
            except Exception as e:
                print(f"    Could not get info: {e}")

            print("\n[2.4] Attempting to click...")
            tab.click()
            print("    ✅ Click executed")

            time.sleep(2)

            # Verify navigation
            print("\n[2.5] Verifying navigation...")
            # Take screenshot to verify
            nav.screenshot("/tmp/after_click.png")
            print("    Screenshot saved: /tmp/after_click.png")

        else:
            print("\n❌ Element not found with resourceId")

            # Try alternative methods
            print("\n[3] Trying alternative: description match...")
            tab2 = nav.device.find(
                descriptionMatches="(?i).*search.*"
            )

            if tab2.exists():
                print("    ✅ Found via description")
                tab2.click()
            else:
                print("    ❌ Not found via description either")

                # Try just clicking by coordinates
                print("\n[4] Trying direct coordinates...")
                print("    Coordinates: x=324, y=2165 (center of search tab)")
                nav.device.click(324, 2165)
                print("    ✅ Clicked at coordinates")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Debug completed")
    print("=" * 60)

if __name__ == "__main__":
    main()
