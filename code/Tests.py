import unittest
from UnrefinedDataFrame import *


# Stores the file path and start of file name for each CSV file
BASE_TEST_DATA_FILE_PATH = "../data/test/TestData"

"""
This class contains the unit tests for the data refinement steps and their helper methods.

These use a set of pre-made test files to demonstrate each step.

For each test, a base data-set is read in and has the steps to test ran on it. It is then compared to the pre-made
data-set to see if it is correct.
"""


class RefinementTest(unittest.TestCase):

    # Testing removal of duplicates
    def test_duplicate_removal(self):
        df1 = load_test_data()
        df2 = pd.read_csv(BASE_TEST_DATA_FILE_PATH + "_NoDupes.csv", dtype=object)

        df1.clean_duplicates()

        # Resetting the index so the comparison can pass
        df1.df.reset_index(inplace=True, drop=True)

        pd.testing.assert_frame_equal(df1.df, df2)

    # Testing updating the headers
    def test_changing_headers(self):
        df1 = load_test_data()
        df2 = pd.read_csv(BASE_TEST_DATA_FILE_PATH + "_NewHeaders.csv", dtype=object)

        df1.set_headers()

        pd.testing.assert_frame_equal(df1.df, df2)

    # Testing cleaning formatting of columns requiring a specific datatype.
    def test_format_cleaning(self):
        df1 = load_test_data()
        df2 = pd.read_csv(BASE_TEST_DATA_FILE_PATH + "_CleanedFormat.csv", dtype=object)

        # Casting the relevant columns in the pre-made dataset so the comparison can pass
        df2['Creation Time'] = pd.to_datetime(df2['Creation Time'], dayfirst=True, errors='coerce')
        df2['Follower Count'] = pd.to_numeric(df2['Follower Count'], errors='coerce', downcast='integer')
        df2['Friend Count'] = pd.to_numeric(df2['Friend Count'], errors='coerce', downcast='integer')

        # Setting the headers first so the format cleaning will work correctly
        df1.set_headers()
        df1.clean_format()

        pd.testing.assert_frame_equal(df1.df, df2)

    # Testing the full refinement and saving process
    def test_refinement(self):
        # The base data-set is refined and its result saved
        unrefined_frame = load_test_data()
        unrefined_frame.clean_data()

        # This result is then loaded in for comparison
        df1 = pd.read_csv(BASE_TEST_DATA_FILE_PATH + "_Unrefined_REFINED.csv", dtype=object)
        df2 = pd.read_csv(BASE_TEST_DATA_FILE_PATH + "_Refined.csv", dtype=object)

        pd.testing.assert_frame_equal(df1, df2)

    # Testing the is_retweet helper method
    def test_is_retweet(self):
        test_string1 = "RT @ Test, text"
        test_string2 = "Test no RT"

        self.assertTrue(is_retweet(test_string1))
        self.assertFalse(is_retweet(test_string2))

    # Testing the is_reply helper method
    def test_is_reply(self):
        test_string = "Testname"
        test_val = None

        self.assertTrue(is_reply(test_string))
        self.assertFalse(is_reply(test_val))

    # Testing the who_to helper method
    def test_who_to(self):
        test_string = "RT @JohnnyTest text"

        self.assertEqual(who_to(test_string), "JohnnyTest")

    # Testing the find_hashtags helper method
    def test_find_hashtags(self):
        # The test data is taken from the original data-set to give a more realistic test
        test_string = "{\"hashtags\":[{\"text\":\"CometLanding\",\"indices\":[54,67]},{\"text\":\"CometWatch\",\"indices\":[69,80]},{\"text\":\"lander\",\"indices\":[81,88]},{\"text\":\"navcam\",\"indices\":[89,96]}],\"symbols\":[],\"user_mentions\":[],\"urls\":[{\"url\":\"http://t.co/cxgu1KKd3s\",\"expanded_url\":\"http://blogs.esa.int/rosetta/2014/12/05/cometwatch-2-december/\",\"display_url\":\"blogs.esa.int/rosetta/2014/1â€¦\",\"indices\":[104,126]}]}"

        self.assertEqual(find_hashtags(test_string), "CometLanding;CometWatch;lander;navcam")

    # Testing the find_mentions helper method
    def test_find_mentions(self):
        # The test data is taken from the original data-set to give a more realistic test
        test_string = "{\"hashtags\":[{\"text\":\"CometLanding\",\"indices\":[25,38]}],\"symbols\":[],\"user_mentions\":[{\"screen_name\":\"EUCouncil\",\"name\":\"EU Council\",\"id\":206717989,\"id_str\":\"206717989\",\"indices\":[3,13]},{\"screen_name\":\"astro_luca\",\"name\":\"Luca Parmitano\",\"id\":290876018,\"id_str\":\"290876018\",\"indices\":[51,62]}],\"urls\":[{\"url\":\"http://t.co/ZjKAgpXhkt\",\"expanded_url\":\"http://ow.ly/FqZCE\",\"display_url\":\"ow.ly/FqZCE\",\"indices\":[108,130]}],\"media\":[{\"id\":540925054033621000,\"id_str\":\"540925054033620992\",\"indices\":[139,140],\"media_url\":\"http://pbs.twimg.com/media/B4HAeH_IcAAUwSv.jpg\",\"media_url_https\":\"https://pbs.twimg.com/media/B4HAeH_IcAAUwSv.jpg\",\"url\":\"http://t.co/6R7yKrQh9I\",\"display_url\":\"pic.twitter.com/6R7yKrQh9I\",\"expanded_url\":\"http://twitter.com/EUCouncil/status/540925056533413888/photo/1\",\"type\":\"photo\",\"sizes\":{\"small\":{\"w\":340,\"h\":340,\"resize\":\"fit\"},\"thumb\":{\"w\":150,\"h\":150,\"resize\":\"crop\"},\"medium\":{\"w\":600,\"h\":600,\"resize\":\"fit\"},\"large\":{\"w\":1024,\"h\":1024,\"resize\":\"fit\"}},\"source_status_id\":540925056533413900,\"source_status_id_str\":\"540925056533413888\"}]}"
        self.assertEqual(find_mentions(test_string), "EUCouncil")

    # Testing the find_apps helper method
    def test_find_apps(self):
        # The test data is taken from the original data-set to give a more realistic test
        test_string = "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>"
        self.assertEqual(find_apps(test_string), "Twitter Web Client")

    # Testing the compare_headers helper method
    def test_compare_headers(self):
        test1 = ["Test1", "Test2", "Test3"]
        test2 = ["Test1", "Test2", "Test3"]
        test3 = ["Test1", "Test2"]
        test4 = ["Test3", "Test2", "Test3"]

        self.assertTrue(compare_headers(test1, test2))
        self.assertFalse(compare_headers(test1, test3))
        self.assertFalse(compare_headers(test1, test4))


# Helper method to create an instance of UnrefinedDataFrame from the base test data
def load_test_data():
    return UnrefinedDataFrame(BASE_TEST_DATA_FILE_PATH + "_Unrefined.csv")

if __name__ == '__main__':
    unittest.main()
