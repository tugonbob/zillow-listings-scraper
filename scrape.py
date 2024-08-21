from homeharvest import scrape_property
from datetime import datetime, timedelta
import sys
import os
from proxy_manager import ProxyManager
import time
import random
from city_manager import CityManager


def generate_date_range(date_from, days=1):
    date_to = date_from + timedelta(days=days)
    return date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")


def random_sleep():
    time_to_sleep = random.uniform(0, 10)
    print(f"Sleeping for {round(time_to_sleep, 1)}")
    time.sleep(time_to_sleep)


def adjust_period_to_city_density(density):
    # period = k / (density + 1)
    k = 100000
    min_value = 10
    max_value = 365

    # calculate period
    period = k // (density + 1)

    # Enforce the minimum and maximum limits
    period = max(min(period, max_value), min_value)

    return period


if __name__ == "__main__":
    proxyManager = ProxyManager()
    cityManager = CityManager()
    cities = cityManager.get_cities_list()
    args = {"days_to_scrape": 10}

    try:
        for city in cities:
            city_name = city["city"] + ", " + city["state_id"]
            filename = f"scraped_data/{city_name}_sold.csv"
            end_day = datetime.now()
            start_day = end_day - timedelta(days=args["days_to_scrape"])
            period = adjust_period_to_city_density(city["density"])

            date = start_day
            properties = None
            last_working_proxy = None

            while date < end_day:
                date_from, date_to = generate_date_range(date, days=period)
                print(city_name + ": " + date_from + " " + date_to)

                # Proxies to try: first the last working one, then the others
                proxies_to_try = (
                    [last_working_proxy] + proxyManager.valid_proxies
                    if last_working_proxy
                    else proxyManager.valid_proxies
                )

                for proxy in proxies_to_try:
                    if proxy is None:
                        continue

                    try:
                        print(f"Trying {proxy}")
                        properties = scrape_property(
                            location="Houston, TX",
                            listing_type="sold",  # or (for_sale, for_rent, pending)
                            date_from=date_from,  # alternative to past_days
                            date_to=date_to,
                            extra_property_data=True,
                            proxy=proxy,
                            radius=100,
                        )

                        if properties is not None:
                            print(
                                f"Number of properties scraped: {len(properties)} for {date_from} to {date_to}"
                            )
                            last_working_proxy = proxy
                            break
                    except KeyboardInterrupt:
                        sys.exit()
                    except:
                        continue

                # refresh proxy list if none of the proxies work
                if properties is None:
                    proxyManager.refresh_valid_proxies()

                properties.to_csv(
                    filename,
                    mode="a",
                    index=False,
                    header=not os.path.exists(filename),
                )

                date += timedelta(days=period + 1)
                random_sleep()  # maybe to avoid bot protection

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
        sys.exit()
