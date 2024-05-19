#!/usr/bin/env python

import sys

from pandas.errors import EmptyDataError

from AnalysedDataSet import AnalysedDataSet

"""
Takes an input filepath to a post-refinement CSV file and runs analysis on it.

The results are output and stored so they can be used in further methods.
"""
if __name__ == '__main__':
    # Validates the number of arguments, outputting an error and exiting if they are incorrect
    if len(sys.argv) != 2:
        print("Incorrect number of arguments input.")
        print("Usage: ./analyseData.py <file_path>")
        sys.exit(0)
    else:
        try:
            # Running the analysis on the CSV data, outputting the results and storing an instance of AnalysedDataSet
            data = AnalysedDataSet(sys.argv[1])
            data.output_results()
        except FileNotFoundError:
            print("File could not be found.")
        except EmptyDataError:
            print("Input file is missing data.")
        except (KeyError, ValueError):
            print("Input file is incorrectly formatted.")
