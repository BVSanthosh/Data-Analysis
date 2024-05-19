import pandas as pd
import folium
from folium.plugins import FastMarkerCluster, HeatMap
import json
from urllib.request import urlopen
import time

# Collect coords into list

# Stores the default path for a CSV file
DEFAULT_FILE_PATH = "../data/CometLanding_REFINED.csv"

# Stores the filepath to the images directory
IMAGE_DIRECTORY = "../images/"

class Geomap:
    # Loads in the data and runs the required analysis on it, storing the results. A default data filepath is provided.
    def __init__(self, file_path=DEFAULT_FILE_PATH):

        # Credentials and urls used to obtain data from the Map API
        self.apiKey = "mHmaGDAV0NE69q6dVAmyfzV2AACpm1NT"
        mapUrl = 'http://{s}.api.tomtom.com/map/1/tile/basic/main/{z}/{x}/{y}.png?view=Unified&key='

        df = pd.read_csv(DEFAULT_FILE_PATH, dtype=object, keep_default_na=False)

        datas = df[df['Coordinates'] != "n/a"]

        # Creating the base map using the map provided by tom-tom API
        # The following section of code was inspired by the article found here:
        # Sandy_4242 (2018). Display TomTom map with folium. [online] Stack Overflow. Available at: https://stackoverflow.com/questions/53415977/display-tomtom-map-with-folium [Accessed 8 Apr. 2022].
        self.markup_map = folium.Map(
            location=[0, 0],
            zoom_start=3,
            tiles=mapUrl + self.apiKey,
            attr='TomTom')

        self.heat_map = folium.Map(
            location=[0, 0],
            zoom_start=3,
            tiles= mapUrl + self.apiKey,
            attr='TomTom')
        # Section ends here

        # Reading the coordinates from the dataframe extracting the useful bits and storing it in a separate list
        self.lister = []
        self.map_data = {}
        for index, values in datas.iterrows():
            vals = values['Coordinates'].replace("loc: ", "")
            geoval = [float(vals.split(',')[0]), float(vals.split(',')[1])]
            self.lister.append(geoval)

        # Removing 0,0 coordinates
        self.lister = list(filter(([0, 0]).__ne__, self.lister))

        # Callback data used to modify the look of the markers on the map
        # The following section of code was inspired by the article found here:
        #OgnjanD (2018). Adding text to Folium FastMarkerCluster markers? [online] Stack Overflow. Available at: https://stackoverflow.com/questions/50661316/adding-text-to-folium-fastmarkercluster-markers [Accessed 8 Apr. 2022].

        cb = ('function (row) {'
              'var marker = L.marker(new L.LatLng(row[0], row[1]), {color: "red"});'
              'var icon = L.AwesomeMarkers.icon({'
              "icon: 'twitter',"
              "iconColor: 'white',"
              "markerColor: 'cadetblue',"
              "prefix: 'fa',"
              "extraClasses: 'fa-rotate-0'"
              '});'
              'marker.setIcon(icon);'
              'return marker};')

        # Section ends here

        # The following section of code was inspired by the code provided at:
        # studres.cs.st-andrews.ac.uk. (n.d.). Web Login Service - Loading Session Information. [online] Available at: https://studres.cs.st-andrews.ac.uk/CS2006/Lectures/Python/W6-15_Maps/W6-15_Maps.pdf.
        # Adding cluster data to mmap
        FastMarkerCluster(data=self.lister, callback=cb).add_to(self.markup_map)
        folium.LayerControl().add_to(self.markup_map)

        # Adding heatmap layer to the second map
        hm_app = HeatMap(self.lister,
                         min_opacity=0.5, radius=20, blur=15, max_zoom=1)

        hm_app.add_to(self.heat_map)
        # Section ends here

    # Returning the markup map for jupyter to illustrate
    def show_markup_map(self):
        return self.markup_map

    # Returning the heat map for jupyter to illustrate
    def show_heat_map(self):
        return self.heat_map

    def top_n_countries(self):
        # Url for coordinate decoder api
        revGeoUrl = 'https://api.tomtom.com/search/2/reverseGeocode/'
        # Number of requests
        # Used as the api limits the number of requests to 5 per second
        print("Starting analysis\nThis may take a while!")
        noreq = 0
        for row in self.lister:
            if noreq % 5 == 0:
                # Halting the search for a second so that the API would not block our access
                time.sleep(1)
            # Rebuilding coordinates (tailored to the API request model)
            # The documentation can be found here:
            # Tomtom.com. (2021). Reverse Geocode | Search API. [online] Available at: https://developer.tomtom.com/search-api/documentation/reverse-geocoding-service/reverse-geocode [Accessed 8 Apr. 2022].
            coords = '' + str(row[0]) + ',' + str(row[1])
            # Reading the values returned and converting it into json data
            getData = urlopen(revGeoUrl + coords + '?key=' + self.apiKey).read()
            jsonTomTomString = json.loads(getData)
            # Accessing the country name field in data
            count = jsonTomTomString['addresses'][0]['address']['country']
            # Adding the country to dictionary if non-existent and incrementing its count if it exists
            if count in self.map_data:
                self.map_data[count] += 1
            else:
                self.map_data[count] = 1
            # Incrementing request count
            noreq += 1
        print("Done!")

    def return_top_n_countries(self, n):
        # If n is greater than the length of the list, its value is reduced to prevent overflows.
        if n >= len(self.map_data):
            n = len(self.map_data) - 1

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.map_data.items(), key=lambda item: item[1], reverse=True)[:n]

    def print_data(self, n):
        # Finds the top 10 countries with the highest number of tweets and outputs them alongside their counts
        print("\nTop ", n, " countries with the most number of tweets about the matter: ")
        for pair in self.return_top_n_countries(n):
            print("\t" + pair[0], ":", pair[1])

