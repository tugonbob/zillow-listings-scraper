import pandas as pd


class CityManager:
    def __init__(self, path="uscities.csv"):
        self.path = path
        self.data = pd.read_csv(path)

    def get_cities_list(self):
        return self.data[["city", "state_id", "density"]].to_dict("records")


if __name__ == "__main__":
    cities = CityManager()
    print(cities.get_cities_list())
