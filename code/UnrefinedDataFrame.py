import pandas as pd
import re

# Stores the default path for a CSV file
DEFAULT_FILE_PATH = "../data/CometLanding.csv"

# Stores the suffix to add for a post-refinement CSV file.
REFINED_SUFFIX = "_REFINED.csv"

# Stores the column headers to be used before adding new headers.
DEFAULT_COLUMN_HEADERS = ["ID", "User", "Text", "Creation Time w/ Timezone", "Creation Time", "Coordinates",
                          "User Language", "Reply User ID", "Reply Username", "User ID", "Reply Status ID", "Source",
                          "Profile Image", "Follower Count", "Friend Count", "Status", "Entities"]

# Stores the column headers to be used after adding new headers.
REFINED_COLUMN_HEADERS = DEFAULT_COLUMN_HEADERS.copy()
REFINED_COLUMN_HEADERS.extend(["Is RT", "Is Reply", "Hashtags", "Mentions", "RT To"])

"""
This class is used to encapsulate the process of reading in a CSV data set and running required refinement on it.

If changes are made, the new data is stored in a new CSV file.

There are helper methods used to assist in refinement and saving the data if any updates were made.
"""


class UnrefinedDataFrame:

    # Loads in the data and runs any required refinement on it, storing any updates. A default data filepath is provided
    def __init__(self, file_path=DEFAULT_FILE_PATH):
        # Reading in the data file and assigning all values to be Strings to prevent loss of data (specifically in IDs).
        self.df = pd.read_csv(file_path, dtype=object)

        # Stores whether any changes have been made to the data set during refinement checks.
        self.has_changed = False

        # Stores the data set's filepath so any updated files can be saved in the same location with a similar name.
        self.file_path = file_path

    # Writes the stored data frame to a CSV file with an updated name
    def write_data_frame(self, file_path):
        # Creates the file path to use to store the new file by combining the original's with the stored suffix.
        # The substring is used to remove the .csv before adding the suffix.
        new_file_path = file_path[:-4] + REFINED_SUFFIX

        # Storing the data in the calculated location and outputting appropriate feedback
        self.df.to_csv(new_file_path, index=False)
        print("Refined data saved to", new_file_path)

    # Runs the refinement methods in order, checks if any changes were made and calls the write method if so.
    def clean_data(self):
        self.clean_duplicates()
        self.set_headers()
        self.clean_format()
        self.add_headers()
        self.encode_data()
        self.replace_empty_with_holder()

        # Checking if changes were made and if so, calling the write method.
        if self.has_changed:
            self.write_data_frame(self.file_path)

    # Removes duplicates from the data frame and uses length comparisons to check if changes have been made.
    def clean_duplicates(self):
        # Storing the length before dropping duplicates to use for later comparison.
        original_length = len(self.df)

        self.df.drop_duplicates(inplace=True)

        # If the length is lower, then the has_changed flag is updated to match
        if len(self.df) < original_length:
            self.has_changed = True

    def encode_data(self):
        self.df['Text'] = self.df['Text'].str.encode('utf-8').str.decode('utf-8-sig', 'ignore')
        self.df['Source'] = self.df['Source'].str.encode('utf-8').str.decode('utf-8-sig', 'ignore')

    def replace_empty_with_holder(self):
        self.df.fillna(value="n/a", inplace=True)

    # Checks if the headers match either of the two valid final formats and updates them to match the correct default if not.
    def set_headers(self):
        if not compare_headers(self.df.columns, REFINED_COLUMN_HEADERS) and not compare_headers(self.df.columns, DEFAULT_COLUMN_HEADERS):
            self.df.columns = DEFAULT_COLUMN_HEADERS

            self.has_changed = True

    # Checks if the Creation Time and Count values are correctly formatted for their data type and removes any that don't.
    # Uses length comparisons to check if changes have been made.
    def clean_format(self):
        # Storing the length before dropping duplicates to use for later comparison.
        original_length = len(self.df)

        # Parses each column to their respective data type, coercing any invalid values to NaN
        self.df['Creation Time'] = pd.to_datetime(self.df['Creation Time'], dayfirst=True, errors='coerce')
        self.df['Follower Count'] = pd.to_numeric(self.df['Follower Count'], errors='coerce', downcast='integer')
        self.df['Friend Count'] = pd.to_numeric(self.df['Friend Count'], errors='coerce', downcast='integer')
        self.df['Source'] = self.df['Source'].map(find_apps)

        # Drops any rows that now have a NaN in any of the 3 columns
        self.df.dropna(subset=['Creation Time', 'Follower Count', 'Friend Count'])

        # If the length is lower, then the has_changed flag is updated to match
        if len(self.df) < original_length:
            self.has_changed = True

    # Adds the calculated columns to the data set if they don't already exist.
    def add_headers(self):
        if not compare_headers(self.df.columns, REFINED_COLUMN_HEADERS):
            # Creates the Is RT column by checking each row's Text to see if it is a retweet
            self.df['Is RT'] = self.df['Text'].map(is_retweet)

            # Creates the Is Reply column by checking each row's Reply Username to see if it is a reply
            self.df['Is Reply'] = self.df['Reply Username'].map(is_reply)

            # Creates the Hashtags column by parsing each row's Entities to find Hashtags
            self.df['Hashtags'] = self.df['Entities'].map(find_hashtags)
            self.df['Mentions'] = self.df['Entities'].map(find_mentions)

            self.df['RT To'] = self.df['Text'].map(who_to)

            # Updating the has_changed flag appropriately
            self.has_changed = True


# These are a set of helper methods used when refining the data

# Parses a value to see if it matches the format of a retweet and returns a boolean to match.
def is_retweet(s):
    # Validates against the value's type to avoid non-String cases causing errors
    if type(s) == str:
        # Uses a Regex search to see if the text matches the format of a retweet and returns true if it does.
        match = re.search("^RT @", s, re.IGNORECASE)
        if match is not None:
            return True

    return False


# Parses an RT To value to find any users retweeted to stored within and returns the list of them as a ; separated
# string
def who_to(s):
    # Validates against the value's type to avoid non-String cases causing errors
    if type(s) == str:
        # Uses a Regex search to see if the text matches the format of a retweet and returns true if it does.
        match = re.findall("^RT @\S*", s, re.IGNORECASE)
        # If there are apps, they are stored in a String with ;'s separating them
        if match is not None:
            result = ""

            for user in match:
                result += user.replace(':', '').strip()

            # The ; after the last app is removed
            return result[4:]


# Parses a Reply Username value to see if it exists and returns a boolean to match.
# Only Reply Tweet contain this value which is why it indicates if a record is a reply or not.
def is_reply(s):
    # Validates against the value's type to see if the value exists or not.
    if type(s) == str:
        return True
    else:
        return False


# Parses an Entities value to find any hashtags stored within and returns the list of them as a ; separated string
def find_hashtags(s):
    # Validates against the value's type to avoid non-String cases causing errors
    if type(s) == str:
        # Uses a Regex search to find all hashtag values stored in the String and groups their value
        match = re.findall("\"text\":\"([a-zA-Z0-9]+)\",", s, re.IGNORECASE)

        # If there are hashtags, they are stored in a String with ;'s separating them
        if match is not None:
            result = ""

            for hashtag in match:
                result += hashtag + ";"

            # The ; after the last hashtag is removed
            return result[:-1]

# Parses an Entities value to find any hashtags stored within and returns the list of them as a ; separated string
def find_mentions(s):
    result = "";
    # Validates against the value's type to avoid non-String cases causing errors
    if type(s) == str:
        # Uses a Regex search to find all hashtag values stored in the String and groups their value
        match = re.findall("\"user_mentions\":.*\",", s, re.IGNORECASE)

        for matches in match:
            res = re.findall("\"screen_name\":\"([a-zA-Z0-9]+)\",", matches, re.IGNORECASE)

            # If there are hashtags, they are stored in a String with ;'s separating them
            if res is not None:
                result = ""

                for mentions in res:
                    result += mentions + ";"

        # The ; after the last hashtag is removed
        return result[:-1]


# Parses a Source value to find apps stored within and returns the list of them as a ; separated string
def find_apps(s):
    if type(s) == str:

        match = re.findall(">.*</", s, re.IGNORECASE)

        # If there are apps, they are stored in a String with ;'s separating them
        if match is not None:
            result = ""

            for app in match:
                result += app + ";"

            # The ; after the last app is removed
            return result[1:-3]


# Helper method that checks if two arrays are both the same length and contain the same values to allow for comparison of dataframe headers
def compare_headers(arr1, arr2):
    if len(arr1) != len(arr2):
        return False
    for i in range(0, len(arr1)):
        if arr1[i] != arr2[i]:
            return False

    return True
