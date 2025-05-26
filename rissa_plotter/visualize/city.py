import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from .utils import ColorMap, LineStyle, get_logo, get_chelsea_font
from .utils import add_month_day_columns, resample_city_data

logo = get_logo()
chelsea_font = get_chelsea_font()
plt.rcParams["font.family"] = chelsea_font.get_name()


class CityPlotter:
    def __init__(self, city_data: pd.DataFrame):
        self.city_data = city_data.set_index("timestamp")
        self.resampled = resample_city_data(self.city_data, frequency="SME")

    def plot_timeseries(self, year: int = None, station: str = None, **kwargs):
        """
        Plots a time series of kittiwake counts at city stations.
        This method visualizes the counts of visible adult kittiwakes and adults on nest
        over time, optionally filtered by year and/or station. The resulting plot includes
        styled axes, a legend, and a logo.
        Parameters
        ----------
        year : int, optional
            The year to filter the data by. If None, data from all years is included.
        station : str, optional
            The station name to filter the data by. If None, data from all stations is aggregated.
        **kwargs
            Additional keyword arguments passed to `plt.subplots()`.
        Returns
        -------
        fig : matplotlib.figure.Figure
            The matplotlib Figure object containing the plot.
        """

        selection = self.resampled.copy()
        title = "Kittiwakes at City Stations"

        if year is not None:
            selection = selection[selection.index.year == year]
            title += f" in {year}"
        if station is not None:
            selection = selection[selection["station"] == station]
            title += f" - station {station}"
        else:
            selection = (
                selection[["adultCount", "aonCount"]].groupby(selection.index).sum()
            )

        fig, ax = plt.subplots(**kwargs)
        selection["adultCount"].plot(
            ax=ax,
            color=ColorMap.c1,
            label="Visible adults",
            linewidth=2,
            linestyle=LineStyle.VisibleAdults,
        )

        selection["aonCount"].plot(
            ax=ax,
            color=ColorMap.c2,
            label="Adults on nest",
            linewidth=2,
            linestyle=LineStyle.AdultsOnNest,
        )
        # Style the axes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylabel("Kittiwake count")
        ax.set_xlabel("")

        # Add legend
        ax.legend(loc="upper left", fontsize=10, frameon=False)

        # Set y-axis limits
        ymax = selection["adultCount"].max() * 1.1
        ax.set_ylim(0, ymax)

        # Set x-axis limits based on year(s)
        if year is not None:
            ax.set_xlim(pd.Timestamp(f"{year}-03-01"), pd.Timestamp(f"{year}-10-31"))
        else:
            first_year = selection.index.year.min()
            last_year = selection.index.year.max()
            ax.set_xlim(
                pd.Timestamp(f"{first_year}-03-01"), pd.Timestamp(f"{last_year}-10-31")
            )

        # Set plot title
        ax.set_title(title, fontsize=14, fontweight="bold")

        # Add logo
        newax = fig.add_axes([0.75, 0.80, 0.15, 0.15], anchor="SE")
        newax.imshow(logo)
        newax.axis("off")

        fig.patch.set_alpha(0.0)
        return fig

    def compare_years(self, station: str = None, **kwargs):
        """
        Plot and compare kittiwake counts across multiple years on a common calendar x-axis.

        For each year in the data, plots both 'Visible adults' and 'Adults on nest' counts,
        aligned by calendar date (month and day), allowing visual comparison of seasonal trends.
        Optionally, restricts comparison to a single station.

        Parameters
        ----------
        station : str, optional
            Name of the station to filter data by. If None, data is aggregated across all stations.
        **kwargs
            Additional keyword arguments passed to `plt.subplots()`.

        Returns
        -------
        matplotlib.figure.Figure
            The matplotlib Figure object containing the plot.
        """

        # Prepare data selection and title
        selection = self.resampled.copy()
        title = "Kittiwakes at City Stations"
        if station is not None:
            selection = selection[selection["station"] == station]
            title += f" - station {station}"
        else:
            selection = (
                selection[["adultCount", "aonCount"]].groupby(selection.index).sum()
            )

        # Add month/day columns for plotting
        add_month_day_columns(selection, inplace=True)
        valid_years = selection["year"].unique()
        color_names = ["c1", "c2", "c3", "c4", "c5", "cream"]
        valid_colors = color_names[: len(valid_years)]

        # Prepare plot
        fig, ax = plt.subplots(**kwargs)
        color_handles = []
        for year, color_name in zip(valid_years, valid_colors):
            color = getattr(ColorMap, color_name)
            color_handles.append(
                mlines.Line2D([], [], color=color, label=str(year), linestyle="-")
            )
            year_data = selection[selection["year"] == year].set_index("plot_date")
            year_data["adultCount"].plot(
                ax=ax,
                label=f"Visible adults {year}",
                linestyle=LineStyle.VisibleAdults,
                color=color,
            )
            year_data["aonCount"].plot(
                ax=ax,
                label=f"Adults on nest {year}",
                linestyle=LineStyle.AdultsOnNest,
                color=color,
            )

        # Style axes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylabel("Kittiwake count")
        ax.set_xlabel("")

        # Add legends
        color_legend = ax.legend(
            handles=color_handles,
            loc="upper left",
            fontsize=10,
            frameon=False,
        )
        ax.add_artist(color_legend)
        ax.legend(
            handles=[
                mlines.Line2D(
                    [],
                    [],
                    color="black",
                    label="Visible adults",
                    linestyle=LineStyle.VisibleAdults,
                ),
                mlines.Line2D(
                    [],
                    [],
                    color="black",
                    label="Adults on nest",
                    linestyle=LineStyle.AdultsOnNest,
                ),
            ],
            loc="lower right",
            fontsize=8,
            frameon=False,
        )

        # Set y and x limits, format x-axis
        ymax = selection["adultCount"].max() * 1.1
        ax.set_ylim(0, ymax)
        ax.set_xlim(pd.Timestamp("2000-03-01"), pd.Timestamp("2000-10-31"))
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b-%d"))
        fig.autofmt_xdate()

        # Set plot title
        ax.set_title(title, fontsize=14, fontweight="bold")

        # Add logo
        newax = fig.add_axes([0.75, 0.80, 0.15, 0.15], anchor="SE")
        newax.imshow(logo)
        newax.axis("off")

        fig.patch.set_alpha(0.0)
        return fig
