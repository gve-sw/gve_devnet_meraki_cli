"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Mark Orszycki <morszyck@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import os
from datetime import datetime
import json
import csv


def generate_json_report(config_changes, data_folder_path):
    """
    This function generates a JSON report of the configuration changes and saves it to a file.

    Parameters:
    config_changes (list): A list of dictionaries representing the configuration changes.
    data_folder_path (str): The path to the folder where the JSON file will be saved.

    Returns:
    str: The path to the JSON file, or None if an error occurred.
    """
    if not config_changes:
        raise ValueError("config_changes is None or empty")  # Raise an exception if config_changes is None or empty

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current timestamp
    json_file_path = os.path.join(data_folder_path, f"config_changes_{timestamp}.json")  # Create the JSON file path

    try:
        if json_file_path:
            with open(json_file_path, 'w') as f:
                json.dump(config_changes, f, indent=4)
        print(f"Configuration changes saved successfully to {json_file_path}.")
    except IOError as e:
        print(f"IOError writing to file {json_file_path}: {e}")
    except TypeError as e:
        print(f"TypeError writing to file {json_file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error writing to file {json_file_path}: {e}")
        return None
    return json_file_path


def generate_csv_report(config_changes, data_folder_path):
    """
    This function generates a CSV report of the configuration changes and saves it to a file.

    Parameters:
    config_changes (list): A list of dictionaries representing the configuration changes.
    data_folder_path (str): The path to the folder where the CSV file will be saved.

    Returns:
    str: The path to the CSV file, or None if an error occurred.
    """
    if not config_changes:
        raise ValueError("config_changes is None or empty")  # Raise an exception if config_changes is None or empty

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current timestamp
    csv_file_path = os.path.join(data_folder_path, f"config_changes_{timestamp}.csv")  # Create the CSV file path

    try:
        with open(csv_file_path, 'w', newline='') as f:
            fieldnames = config_changes[0].keys()  # Get the fieldnames from the first dictionary in the list
            writer = csv.DictWriter(f, fieldnames=fieldnames)  # Create a DictWriter object
            writer.writeheader()  # Write the header row
            for change in config_changes:  # Write each dictionary as a row
                writer.writerow(change)  # Write the dictionary to the CSV file
    except IOError as e:
        print(f"Error writing to file {csv_file_path}: {e}")  # Print the error message
        return None
    print(f"Configuration changes saved successfully to {csv_file_path}.")  # Print a success message
    return csv_file_path


def generate_txt_report(config_changes, data_folder_path):
    """
    This function generates a TXT report of the configuration changes and saves it to a file.

    Parameters:
    config_changes (list): A list of dictionaries representing the configuration changes.
    data_folder_path (str): The path to the folder where the TXT file will be saved.

    Returns:
    str: The path to the TXT file, or None if an error occurred.
    """
    if not config_changes:
        raise ValueError("config_changes is None or empty")  # Raise an exception if config_changes is None or empty

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the current timestamp
    txt_file_path = os.path.join(data_folder_path, f"config_changes_{timestamp}.txt")  # Create the TXT file path

    try:
        with open(txt_file_path, 'w') as f:
            for change in config_changes:
                f.write(f"{change}\n")
    except IOError as e:
        print(f"Error writing to file {txt_file_path}: {e}")
        return None

    print(f"Configuration changes saved successfully to {txt_file_path}.")

    return txt_file_path
