from homeharvest import scrape_property
from datetime import datetime, timedelta
import sys
import os
from proxy_manager import ProxyManager


def generate_date_range(date_from, days=1):
    date_to = date_from + timedelta(days=days)
    return date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")


if __name__ == "__main__":
    proxyManager = ProxyManager()
    args = {"days_to_scrape": 20, "period": 5}

    try:
        filename = f"houston_sold.csv"
        end_day = datetime.now()
        start_day = end_day - timedelta(days=args["days_to_scrape"])
        period = args["period"]

        date = start_day
        properties = None
        while date < end_day:
            date_from, date_to = generate_date_range(date, days=period)
            print(date_from + " " + date_to)

            for proxy in proxyManager.valid_proxies:
                try:
                    print(f"Trying {proxy}")
                    properties = scrape_property(
                        location="Houston, TX",
                        listing_type="sold",  # or (for_sale, for_rent, pending)
                        date_from=date_from,  # alternative to past_days
                        date_to=date_to,
                        extra_property_data=True,
                        proxy=proxy,
                    )

                    if properties is not None:
                        print(
                            f"Number of properties scraped: {len(properties)} for {date_from} to {date_to}"
                        )
                        break
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    continue

            # refresh proxy list if all of them don't work
            if properties is None:
                valid_proxies = proxyManager.refresh_valid_proxies()

            properties.to_csv(
                filename,
                mode="a",
                index=False,
                header=not os.path.exists(filename),
            )

            date += timedelta(days=period + 1)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
        sys.exit()
