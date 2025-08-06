import pandas as pd
import numpy as np
import math
import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter
import matplotlib.lines as mlines

from rissa_plotter import HotelData, util
from .constants import COLORS, SUBHOTELS, CAPACITY

logo = util.get_logo()
chelsea_font = util.get_chelsea_font()
plt.rcParams["font.family"] = chelsea_font.get_name()


class HotelPlotter:
    INVALID_HOTELS = [
        "Hotel 1",
        "Hotel 2",
    ]

    def __init__(self, hotel_data: HotelData, transparent: bool):
        """
        Initialize HotelPlotter with raw city data and prepare resampled version.
        """
        self.data = hotel_data
        self.years = self.data.years
        self.transparent = transparent

    def chick_counts(self, hotels: list, **kwargs):
        """
        Plot stacked bar charts of chick counts per hotel. Only available for type 1 hotels (Hotel 1 to 5).

        Parameters
        ----------
        hotels : list of str, optional
            List of hotel names to include. If None, use all available in the dataset.
        month : int, optional
            Month to filter the data on.
        kwargs : dict
            Additional keyword arguments passed to `plt.subplots`.
        """

        colors = [util.ColorMap.c2, util.ColorMap.c1, util.ColorMap.c6]
        columns = ["one_chick", "two_chicks", "three_chicks"]

        ncols = len(hotels)
        fig, axes = plt.subplots(ncols=ncols, sharey=True, **kwargs)
        if ncols == 1:
            axes = [axes]

        for i, (ax, hotel) in enumerate(zip(axes, hotels)):
            subhotels = SUBHOTELS[hotel]
            data = []
            for subhotel in subhotels:
                sub_data = self.data.chicks_per_nest(subhotel)
                data.append(sub_data)

            # Concatenate and aggregate
            combined = pd.concat(data)
            # TODO: handle case where subhotels is 1
            data = combined.groupby(combined.index).sum()
            data.plot.bar(ax=ax, stacked=True, color=colors)

            # Clean axis aesthetics
            ax.set_ylabel("Number of nests with chicks")
            ax.set_xlabel("")
            ax.set_ylim(0, 35)
            ax.set_title("")  # Clear default pandas title
            ax.legend().remove()
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            # Hide y-axis on all but the first plot
            if i != 0:
                ax.spines["left"].set_visible(False)
                ax.tick_params(axis="y", left=False, labelleft=False)

            # Add hotel label below plot
            ax.text(
                0.5,
                -0.15,
                hotel,
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=10,
            )

            # transparent background
            if self.transparent:
                ax.patch.set_alpha(0.0)

        # Add shared legend
        handles = [
            mpatches.Patch(color=c, label=label.replace("_", " "))
            for c, label in zip(colors, columns)
        ]
        fig.legend(
            handles=handles,
            loc="upper left",
            frameon=False,
            fontsize=8,
            bbox_to_anchor=(0.12, 0.9),
        )

        # transparent background
        if self.transparent:
            fig.patch.set_alpha(0.0)
        # Add logo
        logo_ax = fig.add_axes([0.75, 0.8, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")

        return fig

    def capacity_used(self, hotels: list, year: int, **kwargs):
        """
        Plot the capacity used at a hotel.

        Parameters
        ----------
        year : int, optional
            The year to plot. If None, plot all years.
        hotel : str, optional
            The hotel to plot. If None, plot all hotels.
        **kwargs : dict
            Additional keyword arguments passed to `plt.subplots()`.
        """

        ncols = len(hotels)
        fig, axes = plt.subplots(ncols=ncols, sharey=True, **kwargs)
        if ncols == 1:
            axes = [axes]

        for i, (ax, hotel) in enumerate(zip(axes, hotels)):
            subhotels = SUBHOTELS[hotel]

            active = (
                self.data.total_aons(hotel=subhotels, year=year)
                .isel(timestamp=-2)
                .item()
            )
            capacity = sum(CAPACITY[subhotel] for subhotel in subhotels)

            percentage = active / capacity * 100

            if re.search(r"\b\d(?=\S)", hotel):
                color = util.ColorMap.c4
            else:
                color = util.ColorMap.c2

            if np.isnan(active):
                active = 0

            ax.bar(x=hotel, height=percentage, color=color)
            ax.text(
                x=hotel,
                y=percentage + 2,
                s=int(math.ceil(active)),
                ha="center",
            )

            # Clean axis aesthetics
            ax.set_xlabel("")
            ax.set_ylim(0, 100)
            ax.set_title("")  # Clear default pandas title
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            if i == 0:
                ax.set_ylabel("Capacity used (%)")
            # Hide y-axis on all but the first plot
            if i != 0:
                ax.spines["left"].set_visible(False)
                ax.tick_params(axis="y", left=False, labelleft=False)

            # Set x-tick label: italic if subhotel
            label = ax.get_xticklabels()[0]
            label.set_rotation(90)

            if re.search(r"\b\d(?=\S)", hotel):  # e.g., Hotel 5.1 or Hotel 6A
                label.set_fontsize(7.5)
            else:
                label.set_fontsize(10)

            # transparent background
            if self.transparent:
                ax.patch.set_alpha(0.0)
        fig.suptitle(
            f"Capacity of hotels used for nesting, in {year}",
            fontsize=11,
            fontweight="bold",
        )

        if self.transparent:
            fig.patch.set_alpha(0.0)

        logo_ax = fig.add_axes([0.75, 0.80, 0.15, 0.15], anchor="SE")
        logo_ax.imshow(logo)
        logo_ax.axis("off")

        return fig

    def compare_years(self, hotels: list = None, **kwargs):
        """
        Compare kittiwake counts across years on a common calendar axis.

        Parameters
        ----------
        hotel : str | list, optional
            Filter by hotel.
        **kwargs : dict
            Additional keyword arguments passed to `plt.subplots()`.

        Returns
        -------
        matplotlib.figure.Figure
        """

        title = util.create_hotel_title(hotels)
        years = self.years

        ymax = 0
        handles_1 = []

        fig, ax = plt.subplots(**kwargs)
        for year in years:

            subhotels = []
            for hotel in hotels:
                subhotels.extend(SUBHOTELS.get(hotel, []))

            total_adults = self.data.total_adults(hotel=subhotels, year=year)
            # total_aons = self.data.total_aons(hotel=subhotels, year=year)
            total_chicks = self.data.total_chicks(hotel=subhotels, year=year)
            year = str(year)
            color = COLORS[year]

            xaxis = util.plotting_date(total_adults["timestamp"])

            ax.plot(
                xaxis,
                total_chicks,
                linestyle="-",
                color=color,
                marker=".",
            )

            ax.plot(
                xaxis,
                total_adults,
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

        # Legend 1 - years
        legend_1 = ax.legend(
            handles=handles_1, loc="upper left", fontsize=10, frameon=False
        )
        ax.add_artist(legend_1)

        # legend 2 - type
        handels_2 = [
            mlines.Line2D(
                [],
                [],
                color="black",
                label="Visible chicks",
                linestyle="-",
            ),
            mlines.Line2D(
                [],
                [],
                color="black",
                label="Visible adults",
                linestyle="--",
            ),
        ]
        ax.legend(
            handles=handels_2,
            loc="lower right",
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

    def plot_submissions(self, **kwargs):
        """
        Plot cumulative daily submissions per year for Kittiwake Hotels.
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

        title = "Kittiwake Hotels"
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

    def plot_submissions_per_bin(self, date: str, frequency="SME", **kwargs):
        """
        Plot the number of submissions per hotel for a given semimonthly bin (if frequency is "SME").

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
        counts = counts.drop(index=self.INVALID_HOTELS, errors="ignore")

        title = f"Semimonthly submissions per Hotel - {date}"

        fig, ax = plt.subplots(**kwargs)
        counts["count"].plot.barh(ax=ax, color=util.ColorMap.c4)
        ax.set_xlabel("Number of submissions")

        self._style_plot(ax, fig, title)
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
