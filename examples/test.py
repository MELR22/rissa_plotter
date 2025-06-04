# %%
from rissa_plotter import readers, visualize, HotelData, CityData
import pandas as pd
import ast

# path = "/path/to/your/firebase_credentials.csv"
"""
path = r"c:\work_projects\Rissa\data\ontvangen_phillip\rissa-app-firebase-adminsdk-fbsvc-c66690f67d.json"
city_data = readers.open_city_table(path)
tables = readers.FireBase(path).collections()
"""
path = r"c:\work_projects\Rissa\data\hotel_data.csv"
df = pd.read_csv(path, index_col=0, parse_dates=True)
df["ledgeStatuses"] = df["ledgeStatuses"].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)
hotels = [
    "Hotel 1",
    "Hotel 2",
    "Hotel 3",
    "Hotel 4",
    "Hotel 5.1A",
    "Hotel 5.1B",
    "Hotel 5.1C",
    "Hotel 5.2A",
    "Hotel 5.2B",
    "Hotel 5.2C",
    "Hotel 5.3",
]

years = [2023, 2024, 2025]

hotel_data = HotelData(hotels=hotels, years=years, data=df)
hotel_data.select_on(hotel="Hotel 1")
hp = visualize.HotelPlotter(hotel_data)
fig = hp.plot_chick_counts(figsize=(8, 6), dpi=400, hotels=hotels[:3])
fig2 = hp.plot_submissions(figsize=(10, 6), dpi=400)


# %%
from rissa_plotter import visualize, HotelData, CityData
import pandas as pd
import ast

path = r"c:\work_projects\Rissa\data\city_data.csv"
df = pd.read_csv(path, index_col="timestamp", parse_dates=True)

years = [2023, 2024, 2025]

city_data = CityData(years=years, data=df)
cp = visualize.CityPlotter(city_data)
fig = cp.plot_timeseries(figsize=(8, 6), dpi=400)
fig1 = cp.compare_years(figsize=(8, 6), dpi=400)
fig2 = cp.plot_submissions(figsize=(10, 6), dpi=400)
# %%
