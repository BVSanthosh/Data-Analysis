import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os

# Stores the default path for a CSV file
DEFAULT_FILE_PATH = "../data/CometLanding_REFINED.csv"

# Stores the filepath to the images directory
IMAGE_DIRECTORY = "../images/"


class Networks:
    # Loads in the data and runs the required analysis on it, storing the results. A default data filepath is provided.
    def __init__(self, file_path=DEFAULT_FILE_PATH):

        # Reading in the data file and assigning ID values to be Strings to prevent loss of data.
        self.df = pd.read_csv(file_path, dtype=object, keep_default_na=False)

        # Limiting the dataframe columns to the ones needed
        self.datas = self.df[['Reply Username', 'User', 'RT To', 'Mentions']]

    # Saving the network to an image and showing it in jupyter notebook
    def displayNetwork(self, size):

        print("starting draw")
        plt.figure(1, dpi=50, figsize=(200, 200))
        plt.title("Network of User Interactions")

        # Sampling the data to a given size as the whole data cannot be illustrated in the graph
        samp_data = self.datas.sample(n=size)

        # Empty undirected graph
        self.G = nx.Graph()

        # Adding nodes where a single username is a single node
        self.G.add_nodes_from(self.datas['User'])

        i = 0
        # Adding edges to the graph
        # Where red represents replies
        # Green represents mentions
        # Blue represents retweets
        # The following section of code was inspired by the article found at:
        # timeislove (2014). networkx - change color/width according to edge attributes - inconsistent result. [online] Stack Overflow. Available at: https://stackoverflow.com/questions/25639169/networkx-change-color-width-according-to-edge-attributes-inconsistent-result [Accessed 8 Apr. 2022].
        for index, row in samp_data.iterrows():
            self.G.add_edge(row['User'], row['Reply Username'], color='r')
            self.G.add_edge(row['User'], row['RT To'], color='b')
            self.G.add_edge(row['User'], row['Mentions'], color='g')
            i += 1
        print(i, " nodes")
        # section ends here

        print("added edges")
        self.G.remove_node("n/a")

        # Removing the nodes with 0 interactions to tidy up the graph
        for node, degree in dict(self.G.degree()).items():
            if degree == 0:
                self.G.remove_node(node)
        print("removed empty edges")

        edges = self.G.edges()
        colors = [self.G[u][v]['color'] for u, v in edges]
        nx.draw(self.G, node_size=120, edge_color=colors, font_size=12, with_labels=True, )
        plt.savefig((IMAGE_DIRECTORY + "network.png"), bbox_inches="tight", dpi=40)
        print("saved")
        plt.show()
