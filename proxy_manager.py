from fp.fp import FreeProxy
import requests
import threading
import queue


def check_proxies():
    global q
    global valid_proxies
    while not q.empty():
        proxy = q.get()
        try:
            res = requests.get(
                "http://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=10,
            )
        except:
            continue

        if res.status_code == 200:
            valid_proxies.append(proxy)


def get_valid_proxies():
    print("Getting valid proxies...")
    global q
    global valid_proxies
    workers = 10
    proxies = FreeProxy(https=True).get_proxy_list(repeat=True)

    q = queue.Queue()
    for proxy in proxies:
        q.put(proxy)

    valid_proxies = []
    threads = []

    # Start the threads
    for _ in range(workers):
        thread = threading.Thread(target=check_proxies)
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print(valid_proxies)
    return valid_proxies
