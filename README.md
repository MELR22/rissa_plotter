# Rissa Plotter

A comprehensive tool for plotting and visualizing data from the Rissa CZ Kittiwake project.

## Features

- Import data directly from Firebase
- Interactive and customizable plotting tools
- Consistent Rissa layout and color scheme

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/rissa_plotter.git
cd rissa_plotter
pip install .
```

## Usage

### Data Import

The `readers` module simplifies importing data from Firebase. A credentials file is required.

**Example:**

```python
from readers import FireBase, open_city_table

credentials_path = "/path/to/your/firebase_credentials.csv"

# List all Firebase collections
collections = FireBase(credentials_path).collections()

# Load city data
city_data = open_city_table(credentials_path)
```

### Visualization

The `visualize` module provides tools for visualizing project data with default layouts and color schemes.

**Example:**

```python
from visualize import CityPlotter

# Initialize plotter with city data
cp = CityPlotter(city_data)

# Plot a timeseries for a specific station and year
station = '01'
year = 2023
fig = cp.plot_timeseries(year=year, station=station, figsize=(12, 6), dpi=150)
```

## License

This project is licensed under the MIT License.