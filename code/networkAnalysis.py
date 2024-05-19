#!/usr/bin/env python

import sys

from pandas.errors import EmptyDataError

from Networks import Networks

"""
Takes an input filepath to a post-refinement CSV file and runs network analysis on it.

"""
if __name__ == '__main__':
    # Validates the number of arguments, outputting an error and exiting if they are incorrect
    if len(sys.argv) != 2:
        print("Incorrect number of arguments input.")
        print("Usage: ./networkAnalysis.py <file_path>")
        sys.exit(0)
    else:
        try:
            # Running the analysis on the CSV data
            network_data = Networks(sys.argv[1])
        except ValueError:
            print("Sample size must be an integer value.")
            print("Usage: ./networkAnalysis.py <file_path>")
            sys.exit(0)
        except FileNotFoundError:
            print("File could not be found.")
        except EmptyDataError:
            print("Input file is missing data.")
        except (KeyError, ValueError):
            print("Input file is incorrectly formatted.")

