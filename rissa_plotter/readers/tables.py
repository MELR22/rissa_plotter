from pathlib import Path
import ast
import pandas as pd

from rissa_plotter import HotelData, CityData
from rissa_plotter.readers import FireBase


def _clean_city_data(df: pd.DataFrame) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["adultCount"] = pd.to_numeric(df["adultCount"])
    df["aonCount"] = pd.to_numeric(df["aonCount"])
    df["groupSize"] = (
        pd.to_numeric(df["groupSize"], errors="coerce").fillna(1).astype(int)
    )
    return df


def _clean_hotel_data(df: pd.DataFrame) -> pd.DataFrame:
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")
    df["hotel"] = df["hotel"].replace("Hotel 3 (green)", "Hotel 4")
    df["hotel"] = df["hotel"].replace("Hotel 4 (metal)", "Hotel 4")
    df["ledgeStatuses"] = df["ledgeStatuses"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    df["groupSize"] = (
        pd.to_numeric(df["groupSize"], errors="coerce").fillna(1).astype(int)
    )
    return df


def open_city_table(path: str | Path) -> pd.DataFrame:
    """
    Read a all City data from the Firestore database.

    Parameters
    ----------
    path : str
        Path to the Firebase service account key file.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the data from the city data Firestore collection.
    """

    with FireBase(path) as fb:
        current = _clean_city_data(fb.read_table("submissionsKittiwakesCity"))
        legacy = _clean_city_data(fb.read_table("submissionsKittiwakesCity2324"))

    df = pd.concat([legacy, current], ignore_index=True)
    df = df.sort_values(by=["timestamp", "station"], ascending=[True, True])
    df.reset_index(drop=True, inplace=True)
    df = df.set_index("timestamp")

    columns = [
        "userId",
        "displayName",
        "userEmail",
        "station",
        "timestamp",
        "groupSize",
        "adultCount",
        "aonCount",
        "comment",
    ]

    years = [2023, 2024, 2025]

    return CityData(
        years=years,
        data=df[columns],
    )


def open_hotel_table(path: str | Path) -> pd.DataFrame:
    with FireBase(path) as fb:
        current = _clean_hotel_data(fb.read_table("submissionsKittiwakesHotels"))
        legacy = _clean_hotel_data(fb.read_table("submissionsKittiwakesHotels2324"))

    df = pd.concat([legacy, current], ignore_index=True)
    df = df.sort_values(by=["timestamp", "hotel"], ascending=[True, True])
    df.reset_index(drop=True, inplace=True)
    df = df.set_index("timestamp")

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

    columns = [
        "userId",
        "displayName",
        "userEmail",
        "hotel",
        "groupSize",
        "ledgeStatuses",
        "ledgeComments",
    ]

    return HotelData(
        data=df[columns],
        years=years,
        hotels=hotels,
    )
