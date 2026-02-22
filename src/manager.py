import time
import os
import fetch_scholar 

SLEEP_SECONDS = 1800 

def main():
    print("=== Website Fetcher Manager Started ===")
    while True:
        try:
            fetch_scholar.run()
        except Exception as e:
            print(f"CRITICAL ERROR in Scholar Fetcher: {e}")

        print(f"--- Sleeping {SLEEP_SECONDS}s ---")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    scholar_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(scholar_dir, exist_ok=True)
    main()