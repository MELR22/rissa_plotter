# %%
from rissa_plotter import readers, visualize
import pandas as pd

path = "/path/to/your/firebase_credentials.csv"

city_data = readers.open_city_table(path)
tables = readers.FireBase(path).collections()

cp = visualize.CityPlotter(city_data)
