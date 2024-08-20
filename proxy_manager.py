from fp.fp import FreeProxy
import requests
import threading
import queue
import random


class ProxyManager:
    def __init__(self):
        self._raw_proxies = queue.Queue()
        self._valid_proxies = []

        self.refresh_valid_proxies()

    @property
    def valid_proxies(self):
        random.shuffle(self._valid_proxies)
        return self._valid_proxies

    def refresh_valid_proxies(self):
        print("Getting valid proxies...")
        workers = 10
        proxies = FreeProxy(https=True).get_proxy_list(repeat=True)

        for proxy in proxies:
            self._raw_proxies.put(proxy)

        threads = []

        # Start the threads
        for _ in range(workers):
            thread = threading.Thread(target=self._check_proxies)
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        print(self._valid_proxies)
        return self._valid_proxies

    def _check_proxies(self):
        while not self._raw_proxies.empty():
            proxy = self._raw_proxies.get()
            try:
                res = requests.get(
                    "http://httpbin.org/ip",
                    proxies={"http": proxy, "https": proxy},
                    timeout=10,
                )
            except:
                continue

            if res.status_code == 200:
                self._valid_proxies.append(proxy)


if __name__ == "__main__":
    proxyManager = ProxyManager()
    proxyManager.get_valid_proxies()
