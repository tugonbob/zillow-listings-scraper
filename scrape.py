from homeharvest import scrape_property
from datetime import datetime, timedelta
import sys
import os
import random
from proxy_manager import get_valid_proxies


def generate_date_range(date_from, days=1):
    date_to = date_from + timedelta(days=days)
    return date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")


if __name__ == "__main__":
    try:
        valid_proxies = get_valid_proxies()
        random.shuffle(valid_proxies)

        filename = f"houston_sold.csv"
        end_day = datetime.now()
        start_day = end_day - timedelta(days=20)

        date = start_day

        while date < end_day:
            date_from, date_to = generate_date_range(date, days=5)
            print(date_from + " " + date_to)

            for proxy in valid_proxies:
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
                valid_proxies = get_valid_proxies()
                random.shuffle(valid_proxies)

            properties.to_csv(
                filename,
                mode="a",
                index=False,
                header=not os.path.exists(filename),
            )

            date += timedelta(days=6)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
        sys.exit()
