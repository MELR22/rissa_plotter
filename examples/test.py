# %%
from rissa_plotter import readers, visualize, HotelData, CityData
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# path = "/path/to/your/firebase_credentials.csv"

path = r"c:\work_projects\RissaCS\Kittiwalkers\ontvangen_phillip\rissa-app-firebase-adminsdk-fbsvc-c66690f67d.json"


city_data = readers.open_city_table(path)
hotel_data = readers.open_hotel_table(path)
tables = readers.FireBase(path).collections()


path_hotel = r"c:\work_projects\RissaCS\Kittiwalkers\hotel_data.csv"
df = pd.read_csv(path_hotel, parse_dates=["timestamp"])
hotel_data = HotelData.from_dataframe(df=df)

path_city = r"c:\work_projects\RissaCS\Kittiwalkers\city_data.csv"
df = pd.read_csv(path_city, parse_dates=["timestamp"])
city_data = CityData.from_dataframe(df=df)

hp = visualize.HotelPlotter(hotel_data, transparent=True)
# fig2 = hp.plot_submissions(figsize=(8.27 / 2, 11.69 / 2), dpi=400)
hotels = [
    "Hotel 3",
    "Hotel 4",
    "Hotel 5",
]
fig4 = hp.capacity_used(figsize=(8.27, 11.69 / 2.5), dpi=400, hotels=hotels, year=2025)

fig = hp.chick_counts(
    figsize=(8.27, 11.69 / 2.5), dpi=400, hotels=["Hotel 3", "Hotel 4", "Hotel 5"]
)
fig = hp.compare_years(figsize=(8.27, 11.69 / 2.5), dpi=400, hotels=hotels)

# fig1 = hp.compare_years(figsize=(10, 6), dpi=400, hotel="Hotel 3")

cp = visualize.CityPlotter(city_data, transparent=True)
fig1 = cp.plot_submissions_per_bin(date="31-07-2025", figsize=(8.27, 11.69), dpi=400)
# fig1 = cp.plot_submissions(figsize=(8.27 / 2, 11.69 / 2), dpi=400)
fig2 = cp.compare_years(figsize=(8.27, 11.69 / 2), dpi=400)

# %%
hotel_data.total_aons(hotel=["Hotel 9"], percentile=1.0)
hotel_data.total_chicks(hotel=["Hotel 5.3"], percentile=1.0)
hotel_data.total_nests(hotel=["Hotel 5.2A"])

import matplotlib.dates as mdates

station = "15"
raw = df[df["station"] == station][["timestamp", "adultCount"]].copy()
fig, ax = plt.subplots(figsize=(8.27, 11.69 / 2), dpi=400)

colors = plt.cm.viridis(np.linspace(0, 1, 10))
for idx, perct in enumerate(np.arange(0.1, 1.1, 0.1)):
    temp = city_data.total_adults(station=[station], percentile=perct)
    temp.plot.scatter(ax=ax, color=colors[idx], label=f"Percentile {perct:.1f}")
city_data.total_adults(station=[station], percentile=0.75).plot(
    ax=ax, color="black", label="Percentile 0.75"
)
raw.plot.scatter(
    x="timestamp", y="adultCount", ax=ax, color="grey", label="Raw data", s=10
)

# Draw vertical lines every 1st and 15th of the month
date_min = raw["timestamp"].min()
date_max = raw["timestamp"].max()
all_dates = pd.date_range(date_min, date_max, freq="D")
for dt in all_dates:
    if dt.day == 7 or dt.day == 23:
        ax.axvline(dt, color="red", linestyle="--", linewidth=0.7, zorder=0)

ax.legend(ncols=2, loc="lower right", fontsize=8, frameon=False)
ax.set_title(f"statistics for {station} - adults per day", fontsize=10)
ax.set_xlim(pd.to_datetime("2025-05-01"), pd.to_datetime("2025-08-01"))
# %%

colors = plt.cm.viridis(np.linspace(0, 1, 10))
for idx, perct in enumerate(np.arange(0.1, 1.1, 0.1)):
    temp = hotel_data.total_aons(hotel=["Hotel 4"], percentile=perct)
    print(temp.sel(timestamp="15-05-2025").item())

# %%
