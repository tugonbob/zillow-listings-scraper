import threading
import queue
import requests
import pandas as pd
import random
import sys
from io import StringIO


class ProxyManager:
    def __init__(self, n=5):
        self.valid_proxies = []
        self.raw_proxies = queue.Queue()  # to store proxies that aren't validated
        self.lock = threading.Lock()  # To protect shared data (valid_proxies)
        self.condition = threading.Condition(self.lock)
        self.n = n  # number of valid proxies to get before stopping
        self.current_proxy_index = 0  # To keep track of the current proxy for rotation

    def get_random_proxy(self):
        with self.lock:
            if not self.valid_proxies:
                raise ValueError("No valid proxies available")

            # Get the next proxy in a round-robin fashion
            proxy = self.valid_proxies[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(
                self.valid_proxies
            )
            return proxy

    def refresh_proxy_list(self):
        proxies = self._get_free_proxy_list()

        for p in proxies:
            self.raw_proxies.put(p)

        print("Getting working proxies...")
        for _ in range(self.n):
            threading.Thread(target=self._save_valid_proxies).start()

    def _get_free_proxy_list(self):
        resp = requests.get("https://free-proxy-list.net/")
        df = pd.read_html(StringIO(resp.text))[0]
        df = df[df["Https"] == "yes"]
        df["Proxy"] = df["IP Address"].astype(str) + ":" + df["Port"].astype(str)
        return df["Proxy"].to_list()

    def _save_valid_proxies(self):
        while not self.raw_proxies.empty():
            proxy = self.raw_proxies.get()

            try:
                res = requests.get(
                    "http://httpbin.org/ip",
                    proxies={"http": proxy, "https": proxy},
                )
                print(res.text)
            except:
                continue

            if res.status_code == 200:
                with self.condition:
                    if len(self.valid_proxies) < self.n:
                        print(proxy)
                        self.valid_proxies.append(proxy)
                    if len(self.valid_proxies) >= self.n:
                        self.condition.notify_all()
                        break

        with self.condition:
            if len(self.valid_proxies) < self.n and self.raw_proxies.empty():
                self.condition.notify_all()

    def get_valid_proxies(self):
        with self.condition:
            while len(self.valid_proxies) < self.n:
                self.condition.wait()
        return self.valid_proxies

    def get_random_proxy(self):
        with self.lock:
            if not self.valid_proxies:
                raise ValueError("No valid proxies available")
            # Randomly select a proxy from the list
            proxy = random.choice(self.valid_proxies)
            return proxy

    def make_request_with_proxy(url, proxies):
        for proxy in proxies:
            try:
                response = requests.get(
                    url, proxies={"http": proxy, "https": proxy}, timeout=5
                )
                response.raise_for_status()  # Raise an exception for 4xx/5xx errors
                return response
            except requests.RequestException as e:
                print(f"Proxy {proxy} failed: {e}")
        return None


if __name__ == "__main__":
    proxy_manager = ProxyManager()
    proxy_manager.refresh_proxy_list()
    # valid_proxies = proxy_manager.get_valid_proxies()
    # print("Valid proxies:", valid_proxies)
    # print(proxy_manager.get_random_proxy())
    # sys.exit(0)
