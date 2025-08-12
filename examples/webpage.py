# %%
from rissa_plotter import visualize, readers, CityData, HotelData
import streamlit as st
import pandas as pd
import ast


# ---- Load Data ----


@st.cache_data(ttl=86400)
def load_data_firebase():
    firebase_config = st.secrets["firebase"]
    city_data = readers.open_city_table(dict(firebase_config))
    hotel_data = readers.open_hotel_table(dict(firebase_config))

    return city_data, hotel_data


def load_data_local():
    path = r"c:\work_projects\RissaCS\Kittiwalkers\ontvangen_phillip\rissa-app-firebase-adminsdk-fbsvc-c66690f67d.json"
    city_data = readers.open_city_table(path)
    hotel_data = readers.open_hotel_table(path)

    return city_data, hotel_data


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Chelsea+Market&display=swap');

    /* App-wide font and background */
    .stApp {
        font-family: 'Chelsea Market', cursive !important;
        color: #000000 !important;
        background-color: #FFF8EE !important;
    }
        
    /* Force tab labels text color to black */
    button[role="tab"] {
        color: black !important;
        font-family: 'Chelsea Market', cursive !important;
    }

    /* Active tab label in black (can bold it) */
    button[role="tab"][aria-selected="true"] {
        color: red !important;
        font-weight: bold !important;
    }
    /* Top bar (header) styling */
    header[data-testid="stHeader"] {
        background-color: #FFF8EE !important;
    }

    header[data-testid="stHeader"]::before {
        box-shadow: none !important;
    }

    /* Sidebar background and text */
    section[data-testid="stSidebar"] {
        background-color: #81B080 !important;
    }

    section[data-testid="stSidebar"] .css-1cpxqw2 {
        color: #000000 !important;
        font-family: 'Chelsea Market', cursive !important;
    }

    /* Titles */
    .stTitle, .stHeader, .stSubheader {
        font-family: 'Chelsea Market', cursive !important;
        color: #000000 !important;
    }

    /* Header font sizes */
    h1 {
        font-size: 32px !important;
        font-weight: bold !important;
    }
    h2 {
        font-size: 24px !important;
    }
    h3 {
        font-size: 18px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


city_data, hotel_data = load_data_firebase()

st.sidebar.header("Figure appearance")
transparent = st.sidebar.checkbox("Transparent background", value=True)
dpi = st.sidebar.slider("DPI", min_value=100, max_value=400, value=150, step=10)
width = st.sidebar.slider("Width (In)", min_value=4, max_value=14, value=12, step=1)
height = st.sidebar.slider("Height (In)", min_value=4, max_value=14, value=6, step=1)
figsize = (width, height)

# Convert pixels to inches
cp = visualize.CityPlotter(city_data, transparent=transparent)
hp = visualize.HotelPlotter(hotel_data, transparent=transparent)
tab1, tab2, tab3 = st.tabs(["City Stations", "Hotels", "Submissions"])

with tab1:
    st.title("City Stations")

    # ---- Sidebar Controls ----
    st.sidebar.header("Plot options City Stations")
    station_options = city_data.data["station"].dropna().unique()
    station = st.sidebar.selectbox(
        "Select station (optional)", ["All"] + list(sorted(station_options))
    )

    years = city_data.years
    year = st.sidebar.selectbox("Select year (optional)", ["All"] + sorted(years))

    # Convert input
    station = station if station != "All" else None

    st.header("Compare the monitored years")
    fig2 = cp.compare_years(station=station, figsize=figsize, dpi=dpi)
    st.pyplot(fig2)
    with st.expander("ℹ️ About this figure"):
        st.markdown(
            """
            This dataset compares the number of counted Kittiwakes across multiple years.  
            This figures shows:
            
            - **`Visible Adults`**: All visible adult birds 
            - **`Apperently Occupied Nests`**: when one or more adults observed sitting on a nest 
            
            The observations are aggregated to semi-monthly values (1st and 15th of each month) by taking the max value (this may be an overestimation) at each station of all observations at a specific city station with the closest days to either 1st or 15th of the month. Missing dates are filled with zeros. The most recent count (indicated by circle) may be subjected to change. 
        """
        )

with tab2:
    st.title("Hotels")

    st.sidebar.header("Plot options Hotels")
    hotel_options_t1 = [
        "Hotel 1",
        "Hotel 2",
        "Hotel 3",
        "Hotel 4",
        "Hotel 5",
    ]
    hotels = st.sidebar.multiselect(
        "Select hotels figure chick counts",
        ["All"] + list(sorted(hotel_options_t1)),
        default=hotel_options_t1,
    )

    fig3 = hp.chick_counts(figsize=figsize, dpi=dpi, hotels=hotels)
    st.pyplot(fig3)
    with st.expander("ℹ️ About this figure"):
        st.markdown(
            """
            This figure displays the number of visible Kittiwake chicks observed at the various hotels.  
            You can view chick counts for a specific month or for the entire breeding season.  
            Please note: For the current year, data may not be available for all months yet.
            """
        )

    st.sidebar.header("Plot options Hotels")
    hotel_options_all = [
        "Hotel 1",
        "Hotel 2",
        "Hotel 3",
        "Hotel 4",
        "Hotel 5",
        "Hotel 6",
        "Hotel 7",
        "Hotel 8",
        "Hotel 9",
    ]
    hotels = st.sidebar.multiselect(
        "Select hotels other figures",
        ["All"] + list(sorted(hotel_options_all)),
        default=hotel_options_all,
    )

    fig4 = hp.capacity_used(figsize=figsize, dpi=dpi, hotels=hotels, year=2025)
    st.pyplot(fig4)

    fig5 = hp.compare_years(figsize=figsize, dpi=dpi, hotels=hotels)
    st.pyplot(fig5)

with tab3:
    st.title("Submissions")

    fig6 = cp.plot_submissions(figsize=figsize, dpi=dpi)
    st.pyplot(fig6)
    fig7 = hp.plot_submissions(figsize=figsize, dpi=dpi)
    st.pyplot(fig7)

    start = "2025-04-01"
    end = "2025-08-31"
    semi_monthly = pd.date_range(start=start, end=end, freq="SME").strftime("%d-%m-%Y")

    bin_name = st.sidebar.selectbox("Select bin", list(semi_monthly))

    fig8 = cp.plot_submissions_per_bin(date=bin_name, figsize=figsize, dpi=dpi)
    st.pyplot(fig8)

    fig9 = hp.plot_submissions_per_bin(date=bin_name, figsize=figsize, dpi=dpi)
    st.pyplot(fig9)
