from pathlib import Path
import ast
import pandas as pd

from rissa_plotter import util, HotelData, CityData
from rissa_plotter.readers import FireBase


def _clean_city_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and preprocesses city data in a DataFrame.

    """
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["adultCount"] = pd.to_numeric(df["adultCount"])
    df["aonCount"] = pd.to_numeric(df["aonCount"])
    df["groupSize"] = (
        pd.to_numeric(df["groupSize"], errors="coerce").fillna(1).astype(int)
    )
    df = df.dropna(subset=["adultCount", "aonCount"], how="all")
    return df


def _clean_hotel_t1_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes hotel type 1 data (Hotel 1 to 5), parsing ledge statuses and computing summary columns.

    """
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")
    df["hotel"] = df["hotel"].replace(
        {"Hotel 3 (green)": "Hotel 3", "Hotel 4 (metal)": "Hotel 4"}
    )

    # Parse ledgeStatuses from string to list/dict if needed
    df["ledgeStatuses"] = df["ledgeStatuses"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    # Compute chick counts and nest/adult counts
    chick_cols = ["one_chick", "two_chicks", "three_chicks", "chickCount"]
    df[chick_cols] = df["ledgeStatuses"].apply(
        lambda x: pd.Series(util.count_chicks(x))
    )
    df["adultCount"] = df["ledgeStatuses"].apply(util.count_adults)
    df["nestCount"] = df["ledgeStatuses"].apply(
        lambda x: util.count_nests(x, include_aon=False)
    )
    df["aonCount"] = df["ledgeStatuses"].apply(
        lambda x: util.count_nests(x, include_aon=True)
    )

    # Clean groupSize
    df["groupSize"] = (
        pd.to_numeric(df["groupSize"], errors="coerce").fillna(1).astype(int)
    )

    # Select and cast output columns
    cols = [
        "timestamp",
        "hotel",
        "adultCount",
        "aonCount",
        "nestCount",
        "chickCount",
        "one_chick",
        "two_chicks",
        "three_chicks",
    ]
    df[cols[2:]] = df[cols[2:]].astype(int)
    return df[cols]


def _clean_hotel_t2_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and converts columns in the hotel T2 (hotel 6-9) data DataFrame.

    """
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed")

    cols = ["adultCount", "aonCount", "chickCount"]
    df[cols] = df[cols].apply(pd.to_numeric)
    return df


def open_city_table(path: str | Path, save: bool = False) -> pd.DataFrame:
    """
    Reads and processes city table data from a FireBase database, combining current and legacy data (2023-2024), optionally saving the result to a CSV file.

    Parameters
    ----------
    path : str or Path
        The file path or Path object pointing to the FireBase database.
    save : bool, optional
        If True, exports the processed data to a CSV file for archiving (default is False).
    Returns
    -------
    CityData
        An instance of CityData containing the cleaned and combined city table data with specified columns.

    """
    with FireBase(path) as fb:
        current = _clean_city_data(fb.read_table("submissionsKittiwakesCity"))
        legacy = _clean_city_data(fb.read_table("submissionsKittiwakesCity2324"))

    # Combine current and legacy data
    df = pd.concat([legacy, current], ignore_index=True)
    df = df.sort_values(by=["timestamp", "station"], ascending=[True, True])
    df.reset_index(drop=True, inplace=True)

    columns = [
        "timestamp",
        "station",
        "adultCount",
        "aonCount",
    ]

    # Optional: export to CSV for archiving
    if save:
        df[columns].to_csv(
            "c:/work_projects/RissaCS/Kittiwalkers/city_data.csv", index=False
        )

    return CityData.from_dataframe(df=df[columns])


def open_hotel_table(path: str | Path, save: bool = False) -> pd.DataFrame:
    """
    Reads and processes hotel table data from a Firebase database, combining type 1 and 2 data and old data from previous years (2023-2024),    cleaning the data, and returning a standardized DataFrame or HotelData object.
    Parameters
    ----------
    path : str or Path
        Path to the Firebase credentials or configuration file.
    save : bool, optional
        If True, saves the processed hotel data to a CSV file for debugging or archiving
        (default is False).
    Returns
    -------
    HotelData
        An instance of HotelData containing the cleaned and combined hotel table data with standardized columns.

    """
    with FireBase(path) as fb:
        t1_new = _clean_hotel_t1_data(fb.read_table("submissionsKittiwakesHotels"))
        t1_old = _clean_hotel_t1_data(fb.read_table("submissionsKittiwakesHotels2324"))
        t2 = _clean_hotel_t2_data(fb.read_table("submissionsKittiwakesGeneralHotels"))

    # Combine and sort T1 and T2 data
    df = pd.concat([t1_old, t1_new, t2], ignore_index=True)
    df = df.sort_values(by=["timestamp", "hotel"]).reset_index(drop=True)

    # Expected output columns (ensure all are present in the data)
    columns = [
        "timestamp",
        "hotel",
        "adultCount",
        "aonCount",
        "nestCount",
        "chickCount",
        "one_chick",
        "two_chicks",
        "three_chicks",
    ]

    # Optional: export to CSV for archiving
    if save:
        df[columns].to_csv(
            "c:/work_projects/RissaCS/Kittiwalkers/hotel_data.csv", index=False
        )

    return HotelData.from_dataframe(df=df[columns])
