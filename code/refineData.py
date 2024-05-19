#!/usr/bin/env python

import sys

from pandas.errors import EmptyDataError

from UnrefinedDataFrame import UnrefinedDataFrame

"""
Takes an input filepath to a CSV file and refines the data in it if necessary.
If any refinement takes place, a new file is output.

The results are output and stored so they can be used in further methods.
"""
if __name__ == '__main__':
    # Validates the number of arguments, outputting an error and exiting if they are incorrect
    if len(sys.argv) != 2:
        print("Incorrect number of arguments input.")
        print("Usage: ./refineData.py <file_path>")
        sys.exit(0)
    else:
        try:
            # Running the refinement on the CSV data, outputting if changes are made and storing the new data if so.
            data = UnrefinedDataFrame(sys.argv[1])
            data.clean_data()

            print("Data refinement completed.")
        except FileNotFoundError:
            print("File could not be found.")
        except EmptyDataError:
            print("Input file is missing data.")
        except ValueError:
            print("Input file is of incorrect format.")
