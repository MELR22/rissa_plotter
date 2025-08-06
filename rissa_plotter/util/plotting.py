from importlib.resources import files
import matplotlib.image as mpimg
import matplotlib.font_manager as fm
import re

import pandas as pd
import xarray as xr


class ColorMap:
    cream = "#FFF8EE"
    c1 = "#2A3D45"
    c2 = "#81B080"
    c3 = "grey"
    c4 = "#9BB7C3"
    c5 = "#3F553E"
    c6 = "#fe2300"
    c7 = "#fdf55f"


def get_logo():
    # Get a path-like object to the file inside the package
    logo_path = files("rissa_plotter.visualize.data") / "logo_green.png"
    return mpimg.imread(logo_path)


def get_chelsea_font():
    # Get a path-like object to the file inside the package
    font_path = files("rissa_plotter.visualize.data") / "ChelseaMarket-Regular.ttf"
    fm.fontManager.addfont(font_path)
    return fm.FontProperties(fname=font_path)


def plotting_date(df: xr.DataArray | pd.Series) -> pd.Series:
    """
    Generate 'plot_date' columns for aligning by calendar day across years.

    Parameters
    ----------
    df : xr.DataArray | pd.Series
        DataArray with a 'timestamp' coordinate.

    Returns
    -------
    pd.Series
        Dataseries with 'plot_date'.
    """
    month_day = df.dt.strftime("%m-%d")
    plot_date = pd.to_datetime("2000-" + month_day, format="%Y-%m-%d")

    return plot_date


def create_hotel_title(hotels):
    # Extract just the numbers or names after "Hotel"
    names = [re.sub(r"^Hotel\s*", "", h) for h in hotels]
    if len(names) == 1:
        return f"Kittiwakes at hotels - Hotel {names[0]}"
    elif len(names) == 2:
        return f"Kittiwakes at hotels - Hotel {names[0]} & {names[1]}"
    else:
        return f"Kittiwakes at hotels - Hotel {', '.join(names[:-1])} & {names[-1]}"
