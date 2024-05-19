from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Stores the default path for a CSV file
DEFAULT_FILE_PATH = "../data/CometLanding_REFINED.csv"

# Stores the filepath to the images directory
IMAGE_DIRECTORY = "../images/"

# Stores the DTypes that have to be assigned on loading the file to prevent loss of information in ID's
SPECIFIED_DTYPE = {"ID": object, "Reply User ID": object, "User ID": object, "Reply Status ID": object}

"""
This class is used to do the necessary calculations required to analyse the patterns in user activity.
"""
class AnalyseUserActivity:

    # Gets the csv file and calls helper functions to prepare the dataset for the analysis
    def __init__(self, file_path, name):
        self.df = pd.read_csv(file_path, dtype=SPECIFIED_DTYPE)
        self.name = name
        self.file_path = file_path

        # Calls the helper functions 
        self.filter_out_data()

        # Gets the follower count by accessing the last row which is the row with the latest time
        self.follower_count = self.df.tail(1)['Follower Count'].values[0]
        # Gets the friend count
        self.friend_count = self.df.iloc[-1:]['Friend Count'].values[0]
        # Gets the retweet count
        self.retweet_count = self.df['Is RT'].sum()
        # Gets the reply count
        self.reply_count = self.df['Is Reply'].sum()
        # Gets the tweet count
        self.tweet_count = len(self.df) - self.retweet_count - self.reply_count
        
        # Methods for outputting the data
        self.write_data_frame()
        self.output_data()

    # Writes the stored data frame to a CSV file with an updated name
    def write_data_frame(self):
        # Names the file
        new_file_path = self.file_path[:-4] + "_" + self.name + ".csv"
        # creates the file
        self.df.to_csv(new_file_path, index=True)
        print("Data saved to", new_file_path)

    # Sorts the rows so that they are chronologically ordered
    def filter_out_data(self):
        # Accesses each value in Creation Time and converts it to a datetime type so that it can be ordered
        for num in range(len(self.df)):
            # Accesses the Creation Time column
            currentDate = self.df.loc[num].at['Creation Time']
            if type(currentDate) == str:
                # Converts it into datetime
                convertedDate = datetime.strptime(currentDate, "%Y-%m-%d %H:%M:%S")
                self.df.at[num, 'Creation Time'] = convertedDate

        # Sets User as the index so that a row can be removed by using the value in User
        self.df.set_index('User', inplace=True)

        self.df = self.df.loc[self.name]

        # Sorts the rows bassed on the Creation Time column
        self.df = self.df.sort_values(by='Creation Time', ascending=True)

    # Gets the number of replies as a list that is chronologically ordered to be used to plot the chart
    def generate_reply_count_list(self):
        # list for storing the reply count overtime
        reply_count_list = []
        count = 0

        for row in self.df['Is Reply']:
            if type(row) is bool:
                if row is True:
                    # Increments the counter if it is a reply
                    count += 1
                    # Stores the value in a list
            reply_count_list.append(count)

        return reply_count_list

    # Gets the number of retweets as a list that is chronologically ordered to be used to plot the chart
    def generate_retweet_count_list(self):
        # list for storing the retweet count overtime
        retweet_count_list = []
        count = 0

        for row in self.df['Is RT']:
            if type(row) is bool:
                if row is True:
                    # Increments the counter if it is a retweet
                    count += 1
                    #stores the value in a list
            retweet_count_list.append(count)

        return retweet_count_list

    # Gets the number of tweets as a list that is chronologically ordered to be used to plot the chart
    def generate_tweet_count_list(self):
        # list for storing the tweet count overtime
        tweet_count_list = []
        count = 0
        #for row in self.df['Is RT'].values, self.df['Is Reply'].values:
        for index, row in self.df.iterrows():
            is_rt = row['Is RT']
            is_reply = row['Is Reply']

            # Checks if it isn't a reply or a tweet
            if (type(is_rt) is bool) and (type(is_reply) is bool):
                if (is_rt is False) and (is_reply is False):
                    # Increments the counter if it is a tweet
                    count += 1
                    # Stores the value in a list
            tweet_count_list.append(count)

        return tweet_count_list

    # Plots the chart
    def activity_over_time(self):
        fig = plt.figure(figsize=(20, 8))
        ax = fig.add_axes([0, 0, 1, 1])
        # Names the chart
        fig.suptitle(f'Timeline of User Activity for {self.name}')
        
        # Gets the list of datetime to be used in the x-axis
        dates = self.df["Creation Time"].values

        # Gets all the relevant data to be used in the y-axis
        reply_counts = self.generate_reply_count_list()
        retweet_counts = self.generate_retweet_count_list()
        tweet_counts = self.generate_tweet_count_list()

        # Plots the data with a label for the line
        ax.plot(dates, reply_counts, label="reply count")
        ax.plot(dates, retweet_counts, label="retweet count")
        ax.plot(dates, tweet_counts, label="tweet count")
        # Creaties a legend labelling each line
        ax.legend()

        return fig

    # Outputs the calculated values
    def output_data(self):
        print("For user ", self.name)
        print("\nNumber of Followers:", self.follower_count)
        print("Number of Friends:", self.friend_count)
        print("Number of Tweets:", self.tweet_count)
        print("Number of Retweets:", self.retweet_count)
        print("Number of Replies:", self.reply_count)

    def output_graph(self):
        # Gets the plotted chart
        activity_graph = self.activity_over_time()
        # saves the chart in the given file
        activity_graph.savefig((IMAGE_DIRECTORY + self.name + "_activity_graph.png"), bbox_inches="tight", dpi=300)
