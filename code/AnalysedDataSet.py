import pandas as pd
import calendar
import math

# Stores the default path for a CSV file
DEFAULT_FILE_PATH = "../data/CometLanding_REFINED.csv"

# Stores the DTypes that have to be assigned on loading the file to prevent loss of information in ID's
SPECIFIED_DTYPE = {"ID": object, "Reply User ID": object, "User ID": object, "Reply Status ID": object}

"""
This class is used to encapsulate the process of reading in a post-refinement CSV data set and running analysis on it.

Relevant results are stored in the class for later use.

There are helper methods used to assist in analysis and getting useful output from the data.
"""


class AnalysedDataSet:

    # Loads in the data and runs the required analysis on it, storing the results. A default data filepath is provided.
    def __init__(self, file_path=DEFAULT_FILE_PATH):
        # Reading in the data file and assigning ID values to be Strings to prevent loss of data.
        self.df = pd.read_csv(file_path, dtype=SPECIFIED_DTYPE)

        # Stores the dictionary of Hashtags, Occurrence Count pairs from the data set
        self.hashtags_data = self.analyse_hashtags()

        # Stores the dictionaries of
        # of User, Reply Count pairs from the data set
        self.user_inter_data = self.analyse_user_inter()
        # of Users, Retweet Count pairs from the data set
        self.user_rt_data = self.analyse_user_rt()
        # of Hashtags, Occurrence Count per month pairs from the data set
        self.hashtags_trend = self.analyse_trending_hashtags_in_month()
        # of Users, Interactions (Retweet/Reply) Count pairs per month from the data set
        self.users_trend = self.analyse_trending_users_in_month()
        # of Hashtags, No of replies pairs from the data set
        self.hashtag_repl = self.analyse_top_n_hashtags_replied_to()
        # of Users, Replied/Reply ratio pairs from the data set
        self.user_ratio = self.analyse_top_n_replies_to_replies_ratio()

        # Stores the dictionary of Time, Tweet Count pairs from the data set
        self.timeline_data = self.tweets_per_day()

        # Stores the dictionary of Application, Tweet Count pairs from the data set
        self.app_data = self.tweets_per_app()

        # Stores the number of records in the data set. 1 is subtracted as headers are counted.
        self.record_count = len(self.df) - 1

        # Stores the count for tweets, retweets and replies as calculated from the data.
        self.retweet_count = self.df['Is RT'].sum()
        self.reply_count = self.df['Is Reply'].sum()
        self.tweet_count = self.record_count - self.retweet_count - self.reply_count

        # Stores the count of users, found by counting the number of unique usernames.
        self.user_count = len(self.df['User'].unique())
        self.app_count = len(self.df['Source'].unique())
        self.u_reply_count = len(self.user_inter_data)

        # Stores the per user average for tweets, retweets and replies as calculated from the above data.
        self.tweet_avg = self.tweet_count / self.user_count
        self.tweet_app_avg = self.tweet_count / self.app_count
        self.retweet_avg = self.retweet_count / self.user_count
        self.reply_avg = self.reply_count / self.user_count
        self.reply_per_avg = self.reply_count / self.u_reply_count

    # Processes the String of Hashtags stored in each record in the data set to create a Dictionary matching
    # each to their number of occurrences
    def analyse_hashtags(self):
        hashtag_data = {}

        for row in self.df['Hashtags']:
            # Validating against the value's datatype to avoid NaN values
            if type(row) is str:
                # Splitting the row into individual hashtags
                for hashtag in row.split(";"):
                    # Converting hashtags to lowercase to prevent counting differently capitalised versions separately
                    hashtag = hashtag.lower()

                    # If the hashtag is already stored, increment its count. Otherwise, add it to the dictionary.
                    if hashtag in hashtag_data:
                        hashtag_data[hashtag] += 1
                    else:
                        hashtag_data[hashtag] = 1

        # Returning the finished dictionary
        return hashtag_data

    def get_months(self):
        months = pd.to_datetime(self.df['Creation Time'], dayfirst=True, errors='coerce').dt.month.unique().astype(int)
        months = sorted([x for x in months if not math.isnan(x) and x >= 0])
        return months

    # Processes the String of Hashtags stored in each record in the data set to create a Dictionary matching
    # each to their number of occurrences in each month
    def analyse_trending_hashtags_in_month(self):
        hashtag_data = {}

        months = self.get_months()

        self.df = self.df.reset_index()
        for month in months:
            month_data = {}
            filtered = self.df[
                pd.to_datetime(self.df['Creation Time'], dayfirst=True, errors='coerce').dt.month == month]
            for row in filtered['Hashtags']:
                # Validating against the value's datatype to avoid NaN values
                if type(row) is str and row != "n/a":
                    # Splitting the row into individual hashtags
                    for hashtag in row.split(";"):
                        # Converting hashtags to lowercase to prevent counting differently capitalised versions separately
                        hashtag = hashtag.lower()

                        # If the hashtag is already stored, increment its count. Otherwise, add it to the dictionary.
                        if hashtag in month_data:
                            month_data[hashtag] += 1
                        else:
                            month_data[hashtag] = 1
            hashtag_data[month] = month_data
        # Returning the finished dictionary

        return hashtag_data

    # Processes the user interactions stored in each record in the data set to create a Dictionary matching
    # each to their number of occurrences in each month
    def analyse_trending_users_in_month(self):
        user_data = {}
        months = self.get_months()

        self.df = self.df.reset_index()
        for month in months:
            u_month_data = {}
            filtered = self.df[(pd.to_datetime(self.df['Creation Time'], dayfirst=True, errors='coerce').dt.month == month)]
            for index, row in filtered.iterrows():
                if type(row['RT To']) is str and row['RT To'] != "n/a":
                    if row['RT To'] in u_month_data:
                        u_month_data[row['RT To']] += 1
                    else:
                        u_month_data[row['RT To']] = 1

                if type(row['Mentions']) is str and row['Mentions'] != "n/a":
                    for mention in row['Mentions'].split(";"):
                        mention = mention.replace(':', '')
                        mention = mention.strip()
                        if mention in u_month_data:
                            u_month_data[mention] += 1
                        else:
                            u_month_data[mention] = 1

                if type(row['Reply Username']) is str and row['Reply Username'] != "n/a":
                    if row['Reply Username'] in u_month_data:
                        u_month_data[row['Reply Username']] += 1
                    else:
                        u_month_data[row['Reply Username']] = 1
            user_data[month] = u_month_data
        # Returning the finished dictionary

        return user_data

    # Processes the user replies stored in each record in the data set to create a Dictionary matching
    # each to their number of occurrences
    # Then calculating the ratio of the replied occurrences to reply
    def analyse_top_n_replies_to_replies_ratio(self):
        user_data_replied = {}
        user_data_replied_to = {}

        filtered = self.df[
            (self.df['Is Reply'] == True)]
        for row in filtered['User']:
            if type(row) is str and row != "n/a":
                if row in user_data_replied:
                    user_data_replied[row] += 1
                else:
                    user_data_replied[row] = 1

        for row in filtered['Reply Username']:
            if type(row) is str and row != "n/a":
                if row in user_data_replied_to:
                    user_data_replied_to[row] += 1
                else:
                    user_data_replied_to[row] = 1

        user_data = zipup(user_data_replied_to, user_data_replied)
        # Returning the finished dictionary
        return user_data

    # Processes the hashtag interactions stored in each record in the data set to create a Dictionary matching
    # each to their number of occurrences
    # So what hashtags have been replied to the most
    def analyse_top_n_hashtags_replied_to(self):
        hashtag_data = {}

        filtered = self.df[
                (self.df['Is Reply'] == True)]
        for row in filtered['Reply Status ID']:
            filteredToSTID = self.df[
                (self.df['Reply Status ID'] == row)]
            for row in filteredToSTID['Hashtags']:
                # Validating against the value's datatype to avoid NaN values
                if type(row) is str and row != "n/a":
                    # Splitting the row into individual hashtags
                    for hashtag in row.split(";"):
                        # Converting hashtags to lowercase to prevent counting differently capitalised versions separately
                        hashtag = hashtag.lower()

                        # If the hashtag is already stored, increment its count. Otherwise, add it to the dictionary.
                        if hashtag in hashtag_data:
                            hashtag_data[hashtag] += 1
                        else:
                            hashtag_data[hashtag] = 1
        # Returning the finished dictionary
        return hashtag_data

    # Sorts the dictionary of Hashtag Data and returns the top n values as a list of tuples.
    def top_n_hashtags(self, n):
        # If n is greater than the length of the list, its value is reduced to prevent overflows.
        if n >= len(self.hashtags_data):
            n = len(self.hashtags_data) - 1

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.hashtags_data.items(), key=lambda item: item[1], reverse=True)[:n]

    # Sorts the dictionary of Hashtag reply Data and returns the top n values as a list of tuples.
    def top_n_hashtags_replied_to(self, n):
        # If n is greater than the length of the list, its value is reduced to prevent overflows.
        if n >= len(self.hashtag_repl):
            n = len(self.hashtag_repl) - 1

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.hashtag_repl.items(), key=lambda item: item[1], reverse=True)[:n]

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.hashtag_rt.items(), key=lambda item: item[1], reverse=True)[:n]

    # Sorts the dictionary of ratios and returns the top n values as a list of tuples.
    def top_n_users_ratioed_to(self, n):
        # If n is greater than the length of the list, its value is reduced to prevent overflows.
        if n >= len(self.user_ratio):
            n = len(self.user_ratio) - 1

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.user_ratio.items(), key=lambda item: item[1], reverse=True)[:n]

    # Sorts the dictionary of Hashtag Data and returns the top n values as a list of tuples.
    def print_trending_hashtags_in_month(self, n):
        for month in self.hashtags_trend:
            print("\nTop ", n, " trending hashtags in ", calendar.month_abbr[month])

            # If n is greater than the length of the list, its value is reduced to prevent overflows.
            if n >= len(self.hashtags_trend[month]):
                n = len(self.hashtags_trend[month]) - 1

            # Sorts the dictionary values based upon their count values in descending order and returns the first n
            # values.
            pairs = sorted(self.hashtags_trend[month].items(), key=lambda item: item[1], reverse=True)[:n]
            for pair in pairs:
                print("\t", pair[0], ":", pair[1])

    # Sorts the dictionary of user interaction Data and returns the top n values as a list of tuples.
    def print_trending_users_in_month(self, n):
        for month in self.users_trend:
            print("\nTop ", n, " trending users in ", calendar.month_abbr[month])

            # If n is greater than the length of the list, its value is reduced to prevent overflows.
            if n >= len(self.users_trend[month]):
                n = len(self.users_trend[month]) - 1

            # Sorts the dictionary values based upon their count values in descending order and returns the first n
            # values.
            pairs = sorted(self.users_trend[month].items(), key=lambda item: item[1], reverse=True)[:n]
            for pair in pairs:
                print("\t", pair[0], ":", pair[1])

    # Sorts the dictionary of user interaction Data and returns the top n values as a list of tuples.
    def top_n_user_interactions(self, n):
        # If n is greater than the length of the list, its value is reduced to prevent overflows.
        if n >= len(self.user_inter_data):
            n = len(self.user_inter_data) - 1

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.user_inter_data.items(), key=lambda item: item[1], reverse=True)[:n]

    # Sorts the dictionary of users retweeted Data and returns the top n values as a list of tuples.
    def top_n_user_rt(self, n):
        # If n is greater than the length of the list, its value is reduced to prevent overflows.
        if n >= len(self.user_rt_data):
            n = len(self.user_rt_data) - 1

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.user_rt_data.items(), key=lambda item: item[1], reverse=True)[:n]

    # Sorts the dictionary of applications used Data and returns the top n values as a list of tuples.
    def top_n_apps(self, n):
        # If n is greater than the length of the list, its value is reduced to prevent overflows.
        if n >= len(self.app_data):
            n = len(self.app_data) - 1

        # Sorts the dictionary values based upon their count values in descending order and returns the first n values.
        return sorted(self.app_data.items(), key=lambda item: item[1], reverse=True)[:n]

    # Processes the datetime stored in each row to create a Dictionary matching datetimes to the amount of activity then
    def tweets_per_day(self):
        date_data = {}

        for date in self.df['Creation Time']:
            # Validating against the value's datatype to avoid NaN values
            if type(date) is str:
                # If the datetime is already stored, increment its count. Otherwise, add it to the dictionary.
                if date in date_data:
                    date_data[date] += 1
                else:
                    date_data[date] = 1

        # Returning the finished dictionary
        return date_data

    # Processes the Sources stored in each row in the data set to create a Dictionary matching
    # each to their number of occurrences
    def tweets_per_app(self):
        app_data = {}

        for app in self.df['Source']:
            if type(app) is str:

                if app in app_data:
                    app_data[app] += 1
                else:
                    app_data[app] = 1

            # Returning the finished dictionary
        return app_data

    # Processes the Usernames replied to stored in each row in the data set to create a Dictionary matching
    # each to their number of occurrences
    def analyse_user_inter(self):
        user_inter_data = {}

        for row in self.df['Reply Username']:
            if type(row) is str and row != "n/a":
                # If the username is already stored, increment its count. Otherwise, add it to the dictionary.
                if row in user_inter_data:
                    user_inter_data[row] += 1
                else:
                    user_inter_data[row] = 1

        # Returning the finished dictionary
        return user_inter_data

    # Processes the user retweeted to stored in each row in the data set to create a Dictionary matching
    # each to their number of occurrences
    def analyse_user_rt(self):
        user_rt_data = {}

        for row in self.df['RT To']:
            if type(row) is str:
                # If the hashtag is already stored, increment its count. Otherwise, add it to the dictionary.
                if row in user_rt_data and row != "n/a":
                    user_rt_data[row] += 1
                else:
                    user_rt_data[row] = 1

        # Returning the finished dictionary
        return user_rt_data

    # Outputs the results stored in the instance of the DataSet
    def output_results(self):
        # Results related to the number of records/types of tweet
        print("Total Number of Records:", self.record_count)
        print("\nNumber of Tweets:", self.tweet_count)
        print("Number of Apps:", self.app_count)
        print("Number of Retweets:", self.retweet_count)
        print("Number of Replies:", self.reply_count)

        # Results related to the number of users
        print("\nNumber of Users:", self.user_count)

        print("\nAvg. Tweets per User:", self.tweet_avg)
        print("Avg. Tweets per App:", self.tweet_app_avg)
        print("Avg. Retweets per User:", self.retweet_avg)
        print("Avg. Replying per User:", self.reply_avg)
        print("Avg. Replies per User:", self.reply_per_avg)

        # Finds the top 10 Hashtags and outputs them alongside their counts
        print("\nTop 10 Hashtags: ")
        for pair in self.top_n_hashtags(10):
            print("\t" + pair[0], ":", pair[1])

        # Finds the top 10 Hashtags and outputs them alongside their counts
        print("\nTop 10 Apps used: ")
        for pair in self.top_n_apps(10):
            print("\t" + pair[0], ":", pair[1])

        # Finds the top 10 users replied and outputs them alongside their counts
        print("\nTop 10 users replied to: ")
        for pair in self.top_n_user_interactions(10):
            print("\t" + pair[0], ":", pair[1])

        # Finds the top 10 users retweeted from and outputs them alongside their counts
        print("\nTop 10 users retweeted from: ")
        for pair in self.top_n_user_rt(10):
            print("\t" + pair[0], ":", pair[1])

        # Finds the top 10 trending hashtags in each month and outputs them alongside their counts
        self.print_trending_hashtags_in_month(10)

        # Finds the top 10 trending users in each month and outputs them alongside their counts
        self.print_trending_users_in_month(10)

        # Finds the top 10 Hashtags and outputs them alongside their counts
        print("\nTop 10 Hashtags replied to: ")
        for pair in self.top_n_hashtags_replied_to(10):
            print("\t" + pair[0], ":", pair[1])

        # Finds the top 10 Hashtags and outputs them alongside their counts
        # print("\nTop 10 Hashtags retweeted to: ")
        # for pair in self.top_n_hashtags_retweeted_to(10):
        #     print("\t" + pair[0], ":", pair[1])

        # Finds the top 10 users with highest ratios and outputs them alongside their counts
        print("\nTop 10 users with highest replied to replying ratio: ")
        for pair in self.top_n_users_ratioed_to(10):
            print("\t" + pair[0], ":", pair[1])

# A function which traverses two dictionaries and divides the values of the matching keys
# Returning a new dictionary with the keys and their resulting values
def zipup(dict1, dict2):
    # extracting keys and values
    keys1 = list(dict1.keys())
    keys2 = list(dict1.keys())
    vals2 = list(dict2.values())
    vals1 = list(dict1.values())

    # assigning new values
    res = dict()
    for idx in range(len(keys1)):
        if keys1[idx] in keys2:
            for idy in range(len(keys2)):
                try:
                    if keys1[idx] == keys2[idy]:
                        res[keys1[idx]] = vals2[idy]/vals1[idx]
                except IndexError:
                    # Error handling for case where the method attempts to access indexes beyond what is stored
                    pass

    return res
