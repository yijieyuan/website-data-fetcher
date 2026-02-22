import os
import time
import requests
import fetch_scholar  # This is the script we built to scrape scholar data

# The unique URL from the "Scholar Data Fetcher" monitor you created
KUMA_URL = "http://192.168.1.17:3001/api/push/sVcSs9gXwS?status=up&msg=OK"

def main():
    print("=== Scholar Fetcher Manager Started (30m Interval) ===")
    while True:
        try:
            # 1. Run the scraper
            fetch_scholar.run()
            
            # 2. SUCCESS: Notify Uptime Kuma
            requests.get(KUMA_URL, timeout=10)
            print("Successfully updated Scholar data. Dashboard: Green.")
            
        except Exception as e:
            # 3. FAILURE: Notify Uptime Kuma with the error message
            # This turns the dashboard RED
            error_url = KUMA_URL.replace("status=up", "status=down") + f"&msg={str(e)}"
            try:
                requests.get(error_url, timeout=10)
            except:
                pass
            print(f"Error updating Scholar data: {e}")

        # Sleep for 30 minutes (1800 seconds)
        time.sleep(1800)

if __name__ == "__main__":
    main()