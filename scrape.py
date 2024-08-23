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
    # used to avoid bot detection on consecutive api call with same proxy
    time_to_sleep = random.uniform(0, 5)
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
    args = {"days_to_scrape": 10, "listing_type": "sold"}
    listing_type = args["listing_type"]

    for city in cities:
        # create output path
        city_name = city["city"] + ", " + city["state_id"]
        out_name = city["city"] + "_" + city["state_id"] + ".csv"
        out_path = f"scraped_data/{listing_type}/{out_name}"

        # define start and stop date
        end_day = datetime.now()
        start_day = end_day - timedelta(days=args["days_to_scrape"])

        # define how many days should be included in each scrape call
        period = adjust_period_to_city_density(city["density"])

        # variables to remeber during loop
        date = start_day  # keep track of what date the loop is currently on
        properties = None  # used to track if all proxies failed. This will stay non if all proxies fail. Otherwise, it holds the scraped data
        last_working_proxy = None  # used to remember the last successful proxy to be called immeadiately in the next iter of loop

        # loop through dates
        while date < end_day:
            # generate date range used for scrape call
            date_from, date_to = generate_date_range(date, days=period)
            print("Finding", listing_type, "in", city_name + ":", date_from, date_to)

            # Proxies to try: first the last working one, then the others
            proxies_to_try = (
                [last_working_proxy] + proxyManager.valid_proxies
                if last_working_proxy
                else proxyManager.valid_proxies
            )

            # loop through proxies
            for proxy in proxies_to_try:
                # first proxy in list will be None at init
                if proxy is None:
                    continue

                try:
                    # scrape real estate data with proxy
                    print(f"Trying {proxy}")
                    properties = scrape_property(
                        location=city_name,
                        listing_type=listing_type,  # or (for_sale, for_rent, pending)
                        date_from=date_from,  # alternative to past_days
                        date_to=date_to,
                        extra_property_data=True,
                        proxy=proxy,
                        radius=100,
                    )

                    # check if scrape was successful
                    if properties is not None:
                        print(
                            f"Number of properties scraped: {len(properties)} for {date_from} to {date_to}"
                        )

                        # save successful proxy for next scrape call
                        last_working_proxy = proxy

                        break
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    # if scrape failed, try next proxy
                    continue

            # refresh proxy list if none of the proxies work
            if properties is None:
                proxyManager.refresh_valid_proxies()

            # save scraped data, append to path as csv
            properties.to_csv(
                out_path,
                mode="a",
                index=False,
                header=not os.path.exists(out_path),
            )

            # move current date by period + 1 days. +1 is to avoid overlap of days
            date += timedelta(days=period + 1)
            random_sleep()  # maybe to avoid bot protection
