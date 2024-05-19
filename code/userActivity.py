#!/usr/bin/env python

import sys

from pandas.errors import EmptyDataError

from AnalyseUserActivity import AnalyseUserActivity

"""
Takes as input the filepath and the username to analyse patterns of user activity.

The results that are output consists of calculations and graphs.
"""

if __name__ == '__main__':
    
    # Validates the number of arguments, outputting an error and exiting if they are incorrect
    if len(sys.argv) != 3:
        print("Incorrect number of arguments input.")
        print("Usage: ./userActivity.py <file_path> <username>")
        sys.exit(0)
    else:
        try:
            user_data = AnalyseUserActivity(sys.argv[1], sys.argv[2])
            print("User activity analysed.")
        except FileNotFoundError:
            # Error message if the file is missing 
            print("File could not be found.")
        except EmptyDataError:
            # Error message if the input file doesn't have data
            print("Input file is missing data.")
        except (KeyError, ValueError):
            # Error message if the format of the input file is incorrect
            print("Input file is incorrectly formatted.")
