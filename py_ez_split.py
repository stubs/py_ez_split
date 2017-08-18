#!/usr/bin/env python
""" Python script to automatically split up raw data CSV files into easier
to manage smaller files with header row automatically copied to freshly
split files."""
import os
from subprocess import check_output

SPLIT_FILE_SIZE = 25000

def find_files(raw_path):
    """Function walks top - down through root directory and returns
    list of path to everyfile."""
    filenames = []
    for (path, dirs, files) in os.walk(raw_path):
        for file_ in files:
            file_ = os.path.join(path, file_)
            filenames.append(file_)
    return filenames


def file_line_count(in_file):
    """Function parameter is a string representing a path to a file.
    A subprocess call is made to use unix tool wc to see the line count
    for the file.  A integer for line count is returned."""
    wc_output = check_output(r"wc -l '{}'".format(in_file))
    wc_output = int(wc_output[: wc_output.index(" ")])
    return wc_output


def file_name_divide(in_file):
    """Function splits a input file path into its name and its extension.
    Returns file name with additional underscore appended and file extension."""
    split_file_name = os.path.splitext(in_file)[0] + "_"
    file_ext = os.path.splitext(in_file)[1]
    return split_file_name, file_ext


def file_split(in_file, new_line_count, new_file, file_ext):
    """Function takes input file, reduced line count, new naming
    convention, and file extension as parameters.  Returns True if unix call
    to split successfully executed; False if not."""
    print "Splitting {}...".format(in_file)
    try:
        check_output(r"split -a 1 --additional-suffix={} -l {} '{}' '{}'".format(file_ext, new_line_count, in_file, new_file))
        print "Split successful."
        return True
    except:
        print "Split failed."
        return False


def grab_file_headers(in_file):
    """Function makes a subprocess call to capture the first row of the input
    CSV file. Returns the captured line sans newlines and carriage returns."""
    return check_output(r"head -1 '{}'".format(in_file)).replace("\r\n", "")


def fetch_split_files(split_file_name):
    """Function makes unix ls call to find any files that wildcard match
    input file name pattern.  Returns list of names."""
    ls_file_output = check_output(r"ls '{}'*".format(split_file_name.replace("\\", "/"))).splitlines()
    return ls_file_output


def add_header_to_split_file(in_file_columns, split_file_name):
    """Function makes a unix sed call to insert header row into newly split
    file. Returns True if successful; False otherwise."""
    try:
        check_output(["sed", "-i", r"1s?^?{} \n?".format(in_file_columns), split_file_name])
        return True
    except:
        print "Error inserting header row in {}".format(split_file_name)
        return False


FILE_LIST = find_files(r'.\test_data')
for files_ in FILE_LIST:
    line_count = file_line_count(files_)
    if line_count > 104000:
        file_name, file_extension = file_name_divide(files_)
        file_columns = grab_file_headers(files_)
        if file_split(files_, SPLIT_FILE_SIZE, file_name, file_extension):
            new_split_file_list = fetch_split_files(file_name)
            for itr, split_file in enumerate(new_split_file_list):
                if itr == 0:
                    pass
                else:
                    add_header_to_split_file(file_columns, split_file)
    else:
        print "No need to split {} because it's line count is {}.".format(files_, line_count)
