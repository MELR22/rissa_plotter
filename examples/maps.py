# %%
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import contextily as ctx

from rissa_plotter import util

chelsea_font = util.get_chelsea_font()
plt.rcParams["font.family"] = chelsea_font.get_name()


# Load data
path = r"c:\work_projects\RissaCS\Kittiwalkers\locations.xlsx"
df = pd.read_excel(path, index_col=0)
df.columns = df.columns.astype(str)  # Clean column names

path_mack = r"c:\work_projects\RissaCS\Kittiwalkers\mack building.json"
mack = gpd.read_file(path_mack).to_crs(epsg=3857)

df = df[~((df["2024"] == "empty") & (df["2025"] == "empty"))]
# Classify status
conditions = [
    (df["2024"] == "active") & (df["2025"] == "active"),
    (df["2024"] == "active") & (df["2025"] != "active"),
    (df["2024"] != "active") & (df["2025"] == "active"),
]

catogories = [
    "City station used in 2024 \n and 2025",
    "City station used in 2024 \n and destroyed in 2025",
    "City station new in 2025",
]
df["Status"] = pd.Series("Inactive", index=df.index)
df.loc[conditions[0], "Status"] = catogories[0]
df.loc[conditions[1], "Status"] = catogories[1]
df.loc[conditions[2], "Status"] = catogories[2]

# Convert to GeoDataFrame
df = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
    crs="EPSG:4326",
)
df = df.to_crs(epsg=3857)
deterrents = df[df["deterrents put between 2024 and 2025 breeding seasons"] == "yes"]

# Set colors
color_map = {
    catogories[0]: util.ColorMap.c1,  # blue
    catogories[1]: util.ColorMap.c6,  # red
    catogories[2]: util.ColorMap.c2,  # green
}

# Plot
fig, ax = plt.subplots(figsize=(8.27 / 1.5, 11.69 / 1.5), dpi=400)
mack.plot(
    ax=ax,
    color=util.ColorMap.c6,
    alpha=0.4,
)


for status, color in color_map.items():
    subset = df[df["Status"] == status]

    stations = subset[subset["Type"] == "city station"]
    stations.plot(
        ax=ax,
        markersize=15,
        marker="o",
        color=color,
        label=status,
    )

    hotels = subset[subset["Type"] == "hotel"]
    hotels.plot(
        ax=ax,
        markersize=30,
        marker="^",
        color=color,
        edgecolor="black",
    )

deterrents.plot(
    ax=ax,
    markersize=70,
    marker="*",
    color="none",
    edgecolor="black",
    label="City station with deterrents",
)

# Style the map
ax.axis("off")
legend_1 = ax.legend(
    loc="upper left", frameon=False, fontsize=8, handlelength=1, handleheight=1
)
ax.add_artist(legend_1)

# legend 2 - type
handels = [
    Line2D(
        [0],
        [0],
        marker="^",
        markersize=8,
        color="none",
        markerfacecolor=util.ColorMap.c1,
        label="Hotel active in 2024 and 2025",
    ),
    Line2D(
        [0],
        [0],
        marker="^",
        color="none",
        markersize=8,
        markerfacecolor=util.ColorMap.c6,
        label="Hotel used in 2024 and \n removed in 2025",
    ),
    Line2D(
        [0],
        [0],
        marker="^",
        color="none",
        markersize=8,
        markerfacecolor=util.ColorMap.c2,
        label="Hotel new in 2025",
    ),
    Patch(
        facecolor=util.ColorMap.c6,
        alpha=0.4,
        label="Mack Øst - demolished in 2025 \n (previously not monitored)",
    ),
]
ax.legend(
    handles=handels,
    loc="upper left",
    bbox_to_anchor=(0.0, 0.86),
    fontsize=8,
    frameon=False,
    handlelength=1,
    handleheight=1,
)

ctx.add_basemap(
    ax,
    crs=df.crs.to_string(),
    source=ctx.providers.CartoDB.Positron,
    zoom=16,
    attribution=False,
)

# Add logo
logo = util.get_logo()
fig = ax.get_figure()
logo_ax = fig.add_axes([0.8, 0.04, 0.15, 0.15], anchor="SE")
logo_ax.imshow(logo)
logo_ax.axis("off")

plt.tight_layout()
plt.show()


# %%
from rissa_plotter import CityData, HotelData

group_1 = ["15a", "15b", "15", "14a", "14", "13a", "13b", "12", "11", "10", "09"]
group_2 = [
    "05a",
    "06",
    "06a",
    "07",
    "08",
    "08b",
    "16a",
    "16b",
    "16c",
    "16d",
    "16",
    "17",
    "19",
]
group_3 = [
    "01",
    "02",
    "02b",
    "04b",
    "04",
    "20",
    "20b",
    "20d",
    "20e",
    "21",
    "22",
    "22b",
    "16e",
    "16f",
]

group_4 = ["23", "24", "25", "26", "26b", "26c", "27", "28", "28b", "29"]

group_5 = [
    "30",
    "31",
    "31a",
    "31b",
    "31c",
    "31d",
    "32",
    "32a",
    "32b",
    "32c",
    "32d",
    "32e",
    "32f",
    "33",
    "34",
]


path_city = r"c:\work_projects\RissaCS\Kittiwalkers\city_data.csv"
df = pd.read_csv(path_city, parse_dates=["timestamp"])
city_data = CityData.from_dataframe(df=df)

for group in [group_1, group_2, group_3, group_4, group_5]:
    print(f"Group: {group}")
    print(
        "Total Adults:",
        city_data.total_adults(station=group, percentile=0.75, year=2025)
        .isel(timestamp=-2)
        .item(),
    )
    print(
        "Total AONs:",
        city_data.total_aons(station=group, percentile=0.75, year=2025)
        .isel(timestamp=-2)
        .item(),
    )
    print()

path_hotel = r"c:\work_projects\RissaCS\Kittiwalkers\hotel_data.csv"
df = pd.read_csv(path_hotel, parse_dates=["timestamp"])
hotel_data = HotelData.from_dataframe(df=df)

group_5h = [
    "Hotel 3",
    "Hotel 4",
    "Hotel 5.1A",
    "Hotel 5.1B",
    "Hotel 5.1C",
    "Hotel 5.2A",
    "Hotel 5.2B",
    "Hotel 5.2C",
    "Hotel 5.3",
    "Hotel 8",
    "Hotel 9",
]
group_4h = [
    "Hotel 6L",
    "Hotel 6O",
    "Hotel 6R",
    "Hotel 7L",
    "Hotel 7O",
    "Hotel 7R",
]

for group in [group_4h, group_5h]:
    print(f"Group: {group}")
    print(
        "Total Adults:",
        hotel_data.total_adults(hotel=group, percentile=0.75, year=2025)
        .isel(timestamp=-2)
        .item(),
    )
    print(
        "Total AONs:",
        hotel_data.total_aons(hotel=group, percentile=0.75, year=2025)
        .isel(timestamp=-2)
        .item(),  # take last instead of max count
    )
    print()

# %%
