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

import typer
from typing import Optional, Tuple
from config.config import c
from logger.logrr import lm
from meraki_api.meraki import MerakiOps
from env_manager.em import em
from meraki.exceptions import APIError
from functions.utils import generate_csv_report, generate_json_report
from rich.progress import Progress

DATA_FOLDER_PATH = c.DATA_FOLDER_PATH  # Path to the data folder for csv file output

app = typer.Typer()  # Typer App


class UF:
    """
    Utility Functions class for common functions used in the application.
    """

    @staticmethod
    def prompt_with_choices(prompt: str, choices: list):
        """
        This function prompts the user with a list of choices and returns the selected choice.
        """
        for i, choice in enumerate(choices, start=1):
            # If the choice is a tuple, print both the name and value
            if isinstance(choice, tuple):
                name, value = choice
                lm.lnp(f"{i}. {name}: {value}")
            else:
                lm.lnp(f"{i}. {choice}")
        while True:
            selection = typer.prompt(prompt)
            if selection.isdigit() and 1 <= int(selection) <= len(choices):
                return choices[int(selection) - 1]
            else:
                lm.lnp("Invalid selection. Please try again.", style="error", level="error")

    @staticmethod
    def check_api_key(api_key: Optional[str] = None) -> Tuple[str, str]:
        if not api_key:
            # Get all attributes of the c object that start with 'MERAKI_API_KEY_'
            api_keys = [attr for attr in dir(c) if attr.startswith('MERAKI_API_KEY_')]
            api_key_values = [(key, getattr(c, key)) for key in api_keys]  # Get both the name and value of the API keys

            # Add an option to enter a new API key
            api_key_values.append("Enter a new API key")

            # Prompt the user to select an API key or enter a new one
            selection = UF.prompt_with_choices("Please select an API key or enter a new one", api_key_values)

            # If the user chose to enter a new API key, prompt for it
            if selection == "Enter a new API key":
                api_key = typer.prompt("Please enter the new API key")
                valid, message, org_id, org_name = em.set_meraki_api_key(api_key=api_key)
            else:
                # If the user selected an existing API key, get its value
                _, api_key = selection
                meraki_ops = MerakiOps(api_key=api_key)
                org_id, _ = meraki_ops.get_org_id()  # Get the organization ID
            return api_key, org_id
        else:
            meraki_ops = MerakiOps(api_key=api_key)
            org_id, _ = meraki_ops.get_org_id()  # Get the organization ID
        return api_key, org_id

    @staticmethod
    def validate_timespan(t0: Optional[int], t1: Optional[int], timespan: Optional[int]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        This function validates the timespan, t0, and t1 parameters.
        It raises an exception if the parameters are not valid.
        """
        if (t0 is None or t1 is None) and timespan is None:
            lm.lnp(f"Please provide either a timespan or both t0 and t1.", style="error", level="error")
            raise typer.Exit(1)
        if (t0 is not None and t1 is None) or (t0 is None and t1 is not None):
            lm.lnp(f"[red]If using t0 & t1 instead of timespan, please provide both t0 and t1.", style="error", level="error")
            raise typer.Exit(1)

        return t0, t1, timespan

    @staticmethod
    def common_setup():
        """
        This function sets up the common environment for the application.
        It creates and loads the environment if it's missing and prints the start panel.
        """
        em.create_and_load_env_if_missing()  # Create and load the environment if missing
        lm.print_start_panel(app_name=c.APP_NAME)  # Print the start panel
        # em.ensure_vars_set(var_names=c.REQUIRED_ENV_VARS, callback=em.reload_env)  # Ensure required environment variables are set


@app.callback()
def main_callback():
    """
    This callback is run before any command.
    It sets up the common environment for the application.
    """
    # common_setup()


@app.command()
def list_orgs(api_key: str = typer.Option(None, help="Meraki API key")):
    """
    This command lists all Meraki organizations accessible with the API key.
    """
    api_key, org_id = UF.check_api_key(api_key=api_key)  # API Key check
    meraki_ops = MerakiOps(api_key=api_key)  # Initialize Meraki API
    meraki_ops.get_orgs()  # Get orgs associated with API key


@app.command()
def list_networks(api_key: Optional[str] = None):
    """
    This command lists all networks within a specified Meraki organization.
    If no organization ID is provided, it prompts the user to enter one.
    """
    api_key, org_id = UF.check_api_key(api_key=api_key)
    meraki_ops = MerakiOps(api_key=api_key)
    meraki_ops.list_networks(org_id=org_id)


@app.command()
def create_org(api_key: str = typer.Option(None, help="Meraki API key")):
    """
    This command creates a new Meraki organization.
    It prompts the user to enter the organization name.
    Used to create test organizations.
    """
    api_key, org_id = UF.check_api_key(api_key=api_key)  # API Key check
    meraki_ops = MerakiOps(api_key=api_key)  # Initialize Meraki API
    org_name = typer.prompt("Please enter the name of the new organization")  # Prompt user for name of organization to create
    meraki_ops.create_organization(org_name=org_name)


@app.command()
def create_network(api_key: Optional[str] = None):
    """
    This command creates a new Meraki network.
    It prompts the user to enter the organization ID, network name, and network type.
    """
    api_key, org_id = UF.check_api_key(api_key=api_key)
    meraki_ops = MerakiOps(api_key=api_key)
    network_name = typer.prompt("Please enter the name of the new network")
    network_type = typer.prompt("Please enter the type of the new network (wireless, switch, appliance, systemsManager, camera, celluarGateway)")
    meraki_ops.create_network(org_id=org_id, network_name=network_name, network_type=network_type)


@app.command()
def get_config_changes_org_wide(api_key: Optional[str] = None, timespan: int = 864000, filter_switch: bool = typer.Option(False, help="Filter switch changes")):
    """
    This command gets the configuration changes for all networks in an organization within a specified timespan.
    """
    api_key, org_id = UF.check_api_key(api_key=api_key)
    meraki_ops = MerakiOps(api_key=api_key)
    networks = meraki_ops.get_networks(org_id=org_id)
    if not networks:
        lm.lnp(f"No networks found or unable to list networks for organization ID {org_id}.", style="error")
        raise typer.Exit()

    all_changes = []  # List to store all changes from all networks
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching configuration changes...", total=len(networks))
        for network in networks:
            network_id = network['id']
            config_changes = meraki_ops.fetch_config_changes(org_id, network_id=network_id, timespan=timespan)

            # Filter the changes if filter_switch is True
            if filter_switch:
                config_changes = [change for change in config_changes if 'switch' in change.get('networkUrl', '')]

            if config_changes:
                all_changes.extend(config_changes)  # Append changes to the list

            progress.update(task, advance=1)

    if all_changes:
        generate_csv_report(config_changes=all_changes, data_folder_path=DATA_FOLDER_PATH)
        generate_json_report(config_changes=all_changes, data_folder_path=DATA_FOLDER_PATH)  # Generate a JSON report
    else:
        lm.lnp(f"No configuration changes found for any network in organization ID {org_id}.", style="warning")


@app.command()
def get_config_changes_by_network(api_key: Optional[str] = None, timespan: int = 864000, filter_switch: bool = typer.Option(False, help="Filter switch changes")):
    """
    This command gets the configuration changes for a specific network within a specified timespan.
    """
    api_key, org_id = UF.check_api_key(api_key=api_key)
    meraki_ops = MerakiOps(api_key=api_key)
    try:
        networks = meraki_ops.get_networks(org_id=org_id)  # Get the networks for the organization
        network_id, network_name = meraki_ops.select_network(networks=networks)  # Select a network from the list
        config_changes = meraki_ops.fetch_config_changes(org_id, network_id, timespan)  # Fetch configuration changes for the network

        # Filter the changes if filter_switch is True
        if filter_switch:
            config_changes = [change for change in config_changes if 'switch' in change.get('networkUrl', '')]

        generate_csv_report(config_changes=config_changes, data_folder_path=DATA_FOLDER_PATH)  # Generate a CSV report
        # generate_json_report(config_changes=config_changes, data_folder_path=DATA_FOLDER_PATH)  # Generate a JSON report
    except APIError as e:
        lm.lnp(f"API error fetching configuration changes for organization ID {org_id}. Error: {str(e)}", style="error")
    except Exception as e:
        lm.lnp(f"Error fetching configuration changes for organization ID {org_id}. Error: {str(e)}", style="error")


@app.command()
def get_config_changes_network_list(
        api_key: Optional[str] = None,
        timespan: Optional[int] = None,
        t0: Optional[int] = None, t1: Optional[int] = None,
        filter_switch: bool = typer.Option(False, help="Filter switch changes")
):
    """
    This command gets the configuration changes for a list of networks within a specified timespan.
    If no timespan is provided, it prompts the user to enter the start and end times.
    """
    api_key, org_id = UF.check_api_key(api_key=api_key)
    meraki_ops = MerakiOps(api_key=api_key)

    t0, t1, timespan = UF.validate_timespan(t0, t1, timespan)

    network_list = c.TARGET_NETWORKS  # List of network IDs to fetch configuration changes for (from settings.py)
    for network in network_list:  # Iterate over the network IDs
        network_id = network  # Get the network ID
        try:
            config_changes = meraki_ops.fetch_config_changes(org_id, network_id, timespan)  # Fetch configuration changes for the network id

            # Filter the changes if filter_switch is True
            if filter_switch:
                config_changes = [change for change in config_changes if 'switch' in change.get('networkUrl', '')]

            generate_csv_report(config_changes=config_changes, data_folder_path=DATA_FOLDER_PATH)  # Generate a CSV report
            # generate_json_report(config_changes=config_changes, data_folder_path=DATA_FOLDER_PATH)  # Generate a JSON report

        except APIError as e:
            lm.lnp(f"API error fetching configuration changes for network ID {network_id} in organization ID {org_id}. Error: {str(e)}", style="error")
        except Exception as e:
            lm.lnp(f"Error fetching configuration changes for network ID {network_id} in organization ID {org_id}. Error: {str(e)}", style="error")


if __name__ == "__main__":
    app()
