"""
Debug script - Test different find methods
"""
import sys
from loguru import logger
from src.gramaddict_wrapper.navigation import InstagramNavigator
import uiautomator2 as u2

logger.remove()
logger.add(sys.stdout, level="DEBUG")

def main():
    print("=" * 60)
    print("Debug: Testing Different Find Methods")
    print("=" * 60)

    # Initialize navigator
    nav = InstagramNavigator()
    nav.connect()

    print("\n[Method 1] Using DeviceFacade (GramAddict)")
    try:
        tab = nav.device.find(resourceId="com.instagram.android:id/search_tab")
        print(f"  Result: {tab.exists()}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n[Method 2] Using raw uiautomator2")
    try:
        d = u2.connect()
        tab = d(resourceId="com.instagram.android:id/search_tab")
        print(f"  Result: {tab.exists()}")
        if tab.exists():
            print(f"  Info: {tab.info}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n[Method 3] Using className + text pattern")
    try:
        d = u2.connect()
        tab = d(className="android.widget.FrameLayout", descriptionContains="search")
        print(f"  Result: {tab.exists()}")
        if tab.exists():
            print(f"  Info: {tab.info}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n[Method 4] Find all tabs and list them")
    try:
        d = u2.connect()
        tabs = d(resourceIdMatches=".*tab$")
        count = tabs.count
        print(f"  Found {count} tabs")

        for i in range(min(count, 10)):
            tab = tabs[i]
            try:
                info = tab.info
                print(f"    [{i}] {info.get('resourceName')} - {info.get('contentDescription')}")
            except:
                pass
    except Exception as e:
        print(f"  Error: {e}")

    print("\n[Method 5] Direct coordinate click test")
    try:
        d = u2.connect()
        # Search tab coordinates: [216,2148][432,2182]
        # Center: x=324, y=2165
        print("  Clicking at x=324, y=2165...")
        d.click(324, 2165)
        print("  ✅ Clicked!")

        import time
        time.sleep(2)

        # Check if we're on search screen
        print("  Checking current screen...")
        # Save screenshot
        d.screenshot("/tmp/after_coordinate_click.png")
        print("  Screenshot: /tmp/after_coordinate_click.png")

    except Exception as e:
        print(f"  Error: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
