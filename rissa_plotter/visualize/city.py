import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.dates import DateFormatter

from rissa_plotter import util
from rissa_plotter import CityData
from .constants import COLORS

logo = util.get_logo()
chelsea_font = util.get_chelsea_font()
plt.rcParams["font.family"] = chelsea_font.get_name()


class CityPlotter:
    INVALID_STATIONS = [
        "02b",
        "04b",
        "05",
        "06",
        "05a",
        "06a",
        "07",
        "15b",
        "18",
        "20",
        "22b",
        "26",
        "27",
    ]

    def __init__(self, city_data: CityData, transparent: bool):
        """
        Initialize CityPlotter with raw city data and prepare resampled version.
        """
        self.data = city_data
        self.years = self.data.years
        self.transparent = transparent

    def plot_timeseries(self, year: int = None, station: str = None, **kwargs):
        """
        Plot time series of kittiwake counts at city stations.

        Parameters
        ----------
        year : int, optional
            Filter the data by year.
        station : str, optional
            Filter the data by station.
        **kwargs : dict
            Additional keyword arguments passed to `plt.subplots()`.

        Returns
        -------
        matplotlib.figure.Figure

        """
        total_adults = self.data.total_adults(station=station, year=year)
        total_aons = self.data.total_aons(station=station, year=year)

        title = "Kittiwakes at City Stations"
        if year:
            title += f" in {year}"
        if station:
            title += f" - station {station}"

        fig, ax = plt.subplots(**kwargs)

        total_adults.plot(
            ax=ax,
            color=COLORS["adults"],
            label="Visible adults",
            linestyle="-",
            marker=".",
        )

        total_aons.plot(
            ax=ax,
            color=COLORS["aons"],
            label="Apparently occupied nests",
            linestyle="--",
            marker=".",
        )

        # legend
        ax.legend(loc="upper left", fontsize=10, frameon=False)

        # axis layout
        ax.set_ylabel("Count")
        ax.set_xlabel("")
        ax.set_ylim(0, total_adults.max() * 1.1)

        if year is None:
            start = pd.Timestamp(f"{self.years[0]}-03-01")
            end = pd.Timestamp(f"{self.years[-1]}-10-31")
            ax.set_xlim(start, end)
        else:
            ax.set_xlim(pd.Timestamp(f"{year}-03-01"), pd.Timestamp(f"{year}-10-31"))

        # general_layout
        self._style_plot(
            ax,
            fig,
            title,
        )

        return fig

    def compare_years(self, station: str = None, **kwargs):
        """
        Compare kittiwake counts across years on a common calendar axis.

        Parameters
        ----------
        station : str, optional
            Filter by station.
        **kwargs : dict
            Additional keyword arguments passed to `plt.subplots()`.

        Returns
        -------
        matplotlib.figure.Figure

        """
        title = "Kittiwakes at City Stations"
        if station:
            title += f" - station {station}"

        years = self.years

        ymax = 0
        handles_1 = []

        fig, ax = plt.subplots(**kwargs)
        for year in years:
            total_adults = self.data.total_adults(station=station, year=year)
            total_aons = self.data.total_aons(station=station, year=year)
            year = str(year)
            color = COLORS[year]

            xaxis = util.plotting_date(total_adults["timestamp"])

            ax.plot(
                xaxis,
                total_adults,
                linestyle="-",
                color=color,
                marker=".",
            )

            ax.plot(
                xaxis,
                total_aons,
                linestyle="--",
                color=color,
                marker=".",
            )

            yearly_max = total_adults.max().item()
            if yearly_max > ymax:
                ymax = yearly_max

            handles_1.append(
                mlines.Line2D([], [], color=color, label=year, linestyle="-")
            )

        # legend 1 - years
        legend_1 = ax.legend(
            handles=handles_1, loc="upper left", fontsize=10, frameon=False
        )
        ax.add_artist(legend_1)

        # legend 2 - type
        handles_2 = [
            mlines.Line2D([], [], color="black", label="Visible adults", linestyle="-"),
            mlines.Line2D(
                [],
                [],
                color="black",
                label="Apparently occupied \n nests",
                linestyle="--",
            ),
        ]
        ax.legend(
            handles=handles_2,
            loc="upper right",
            bbox_to_anchor=(1, 0.9),
            fontsize=8,
            frameon=False,
        )

        # axis layout
        ax.set_ylabel("Count")
        ax.set_xlabel("")
        ax.set_ylim(0, ymax * 1.1)
        ax.set_xlim(pd.Timestamp("2000-04-01"), pd.Timestamp("2000-10-31"))
        ax.xaxis.set_major_formatter(DateFormatter("%b-%d"))
        fig.autofmt_xdate()

        # general_layout
        self._style_plot(
            ax,
            fig,
            title,
        )

        return fig

    def plot_submissions_per_station(self, **kwargs):
        last_year = self.years[-1]

        yearly_submissions = self.data.yearly_submissions()

        mask = yearly_submissions["year"] == last_year
        selection = yearly_submissions[mask].set_index(["station"])
        selection = selection.drop(index=self.INVALID_STATIONS, errors="ignore")
        selection = selection.sort_index(ascending=False)

        title = f"Submissions per city station in {last_year}"
        fig, ax = plt.subplots(**kwargs)
        selection["count"].plot.barh(ax=ax, color=util.ColorMap.c4)

        ax.set_xlabel("Number of submissions")

        self._style_plot(
            ax,
            fig,
            title,
        )

    def plot_submissions_per_bin(self, date: str, frequency="SME", **kwargs):
        """
        Plot the number of submissions per city station for a given semimonthly bin (if frequency is "SME").

        Parameters
        ----------
        date : str
            The date representing the semimonthly bin to plot, in "%d-%m-%Y".
        **kwargs : dict
            Additional keyword arguments passed to `plt.subplots()`.

        Returns
        -------
        matplotlib.figure.Figure

        """
        counts = self.data.submissions_per_bin(frequency=frequency, date=date)
        counts = counts.drop(index=self.INVALID_STATIONS, errors="ignore")

        title = f"Semimonthly submissions per City Station - {date}"

        fig, ax = plt.subplots(**kwargs)
        counts["count"].plot.barh(ax=ax, color=util.ColorMap.c4)
        ax.set_xlabel("Number of submissions")

        self._style_plot(ax, fig, title)
        return fig

    def plot_submissions(self, **kwargs):
        """
        Plot cumulative daily submissions per year for Kittiwake City Stations.
        This method generates a line plot showing the cumulative number of submissions
        per day for each year in the dataset. Each year's data is plotted with a distinct color,
        and the maximum submission count for each year is annotated on the plot.
        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments passed to `matplotlib.pyplot.subplots`.
        Returns
        -------
        fig : matplotlib.figure.Figure
            The matplotlib Figure object containing the plot.

        """
        years = self.data.years

        title = "Kittiwake City Stations"
        daily_submissions = self.data.daily_submissions()

        fig, ax = plt.subplots(**kwargs)
        for year in years:
            yearly_data = daily_submissions[daily_submissions["year"] == year]
            color = COLORS[str(year)]

            xaxis = util.plotting_date(yearly_data["timestamp"])

            ax.plot(
                xaxis,
                yearly_data["count"],
                color=color,
                label=str(year),
            )

            maxx = xaxis.max()
            maxy = yearly_data["count"].max()
            ax.text(maxx, maxy + 5, s=maxy, c=color)

        # Format plot
        ax.set_ylabel("Cumulative submissions per year")
        ax.set_xlabel("")
        ax.set_xlim(pd.Timestamp("2000-04-01"), pd.Timestamp("2000-9-30"))
        ax.set_ylim(0, 1400)
        ax.xaxis.set_major_formatter(DateFormatter("%b-%d"))
        fig.autofmt_xdate()

        ax.legend(frameon=False, loc="upper left")

        # general_layout
        self._style_plot(
            ax,
            fig,
            title,
        )
        return fig

    def _style_plot(self, ax, fig, title):
        """
        Shared styling for plots.
        """
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_title(title, fontsize=11, fontweight="bold")

        # transparant background
        if self.transparent:
            ax.patch.set_alpha(0.0)
            fig.patch.set_alpha(0.0)

        # Add logo
        fig = ax.get_figure()
        logo_ax = fig.add_axes([0.75, 0.80, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")
