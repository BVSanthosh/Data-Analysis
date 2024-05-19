#!/usr/bin/env python

import sys
from urllib.error import HTTPError

from pandas.errors import EmptyDataError

from Geomap import Geomap

"""
Takes an input filepath to a post-refinement CSV file and runs network analysis on it.

"""
if __name__ == '__main__':
    # Validates the number of arguments, outputting an error and exiting if they are incorrect
    if len(sys.argv) != 2:
        print("Incorrect number of arguments input.")
        print("Usage: GeomapRun.py <file_path>")
        sys.exit(0)
    else:
        try:
            # Running the analysis on the CSV data
            map_data = Geomap(sys.argv[1])
        except FileNotFoundError:
            print("File could not be found.")
        except EmptyDataError:
            print("Input file is missing data.")
        except (KeyError, ValueError):
            print("Input file is incorrectly formatted.")
        except HTTPError:
            print("API could not be accessed, please try again later.")


