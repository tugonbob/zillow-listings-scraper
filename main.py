from homeharvest import scrape_property
from datetime import datetime, timedelta
from proxy_manager import ProxyManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os


def generate_date_range(date_from, days=1):
    date_to = date_from + timedelta(days=days)
    return date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")


def scrape_task(date_from, date_to, proxy):
    try:
        print(f"Trying proxy {proxy} for date range {date_from} to {date_to}")

        properties = scrape_property(
            location="Houston, TX",
            listing_type="sold",  # or (for_sale, for_rent, pending)
            date_from=date_from,  # alternative to past_days
            date_to=date_to,
            proxy=proxy,
            extra_property_data=True,
        )
        print(
            f"Number of properties scraped: {len(properties)} for {date_from} to {date_to}"
        )
        return properties
    except Exception as e:
        print(f"Error with proxy {proxy}: {e}")
        return None


if __name__ == "__main__":
    try:
        proxies = ProxyManager(n=10)
        proxies.refresh_proxy_list()
        valid_proxies = proxies.get_valid_proxies()

        filename = f"houston_sold.csv"
        start_day = datetime.now()
        end_day = start_day - timedelta(days=10)

        date = start_day
        with ThreadPoolExecutor(max_workers=5) as executor:
            while date > end_day:
                date_from, date_to = generate_date_range(date, days=0)
                future_to_proxy = {
                    executor.submit(scrape_task, date_from, date_to, proxy): proxy
                    for proxy in valid_proxies
                }

                for future in as_completed(future_to_proxy):
                    try:
                        properties = future.result()
                        if properties is not None:
                            # Cancel remaining tasks once one is successful
                            for f in future_to_proxy:
                                if not f.done():
                                    f.cancel()
                            properties.to_csv(
                                filename,
                                mode="a",
                                index=False,
                                header=not os.path.exists("aaa.csv"),
                            )
                            print(properties.head())
                            break  # Exit the loop for the current date range once successful
                    except Exception as e:
                        continue

                date -= timedelta(days=1)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
        sys.exit()
