import pandas as pd

df = pd.read_csv(
    "/Users/joshuagao/Documents/GitHub/UH/zillow-listings-scraper/houston_sold.csv"
)


duplicates = df[df.duplicated(keep=False)]

print(len(duplicates))
