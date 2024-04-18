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

from rich.prompt import Prompt
from meraki.exceptions import APIError

import meraki
from app.config.config import c
from app.logger.logrr import lm
import threading


class MerakiOps:
    """
    This class encapsulates operations related to the Meraki API.
    It follows the Singleton design pattern to ensure that only one instance of this class exists.
    """

    _instance = None  # Singleton instance
    _lock = threading.Lock()  # Lock for thread safety

    def __new__(cls, *args, **kwargs):
        """
        This method ensures that only one instance of this class is created.
        It is thread-safe, meaning it can be used in multi-threaded environments.
        """
        with cls._lock:  # Ensure thread safety
            if not cls._instance:  # If the instance does not exist
                cls._instance = super(MerakiOps, cls).__new__(cls)  # Create a new instance
        return cls._instance  # Return the instance

    def __init__(self, api_key=None):
        """
        This method initializes the MerakiOps instance.
        It takes an optional API key as a parameter. If no API key is provided, it uses the default API key from the configuration.
        """
        self.api_key = api_key or c.MERAKI_API_KEY  # Initialize the API key
        self.dashboard = None   # Initialize the dashboard
        self._initialized = False   # Initialize the initialized flag
        self.initialize_dashboard()  # Initialize the dashboard

    def initialize_dashboard(self):
        """
        This method initializes the Meraki Dashboard API with the provided API key.
        It handles any API errors that may occur during initialization.
        """
        try:
            self.dashboard = meraki.DashboardAPI(  # Initialize the dashboard
                api_key=self.api_key,  # API key
                suppress_logging=True,  # Optional: suppress API logging
                caller=c.APP_NAME,  # Optional: provide a custom user-agent string
                maximum_retries=5  # Retry up to 5 times
            )
            self._initialized = True  # Set the initialized flag to True
        except APIError as e:
            self._initialized = False
            lm.lnp(f"Error with Meraki API: {e}", level="error", style="error")
        except Exception as e:
            self._initialized = False
            lm.lnp(f"General error initializing Meraki Dashboard: {e}", level="error", style="error")

    def validate_api_key(self):
        """
        This method validates the Meraki API Key by attempting to list the organizations.
        It returns a tuple where the first element is a boolean indicating the validity of the API key and the second element is a message describing the result.
        """
        if not self.dashboard:
            return False, "Dashboard not initialized."
        try:
            orgs = self.dashboard.organizations.getOrganizations()
            if orgs:
                return True, "Meraki API Key is valid."
            else:
                return False, "No organizations found with the provided API key."
        except meraki.APIError as e:
            return False, f"API Error: {e}"

    @classmethod
    def get_instance(cls) -> 'MerakiOps':
        """
        This method returns a singleton instance of MerakiOps.
        If the instance does not exist, it creates a new one.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_orgs(self):
        """
        This method gets all the Meraki organizations accessible with the API key.
        """
        # lm.p_panel("Fetching Meraki organizations...", style="meraki", )
        with lm.console.status("[bold green]Fetching Meraki Organizations....", spinner="dots"):
            orgs = self.dashboard.organizations.getOrganizations()
        return orgs

    @staticmethod
    def list_orgs(orgs: list) -> None:
        """
        This method fetches and prints all Meraki organizations accessible with the API key.
        """
        if orgs:
            lm.lnp("Organizations:")
            for org in orgs:
                lm.lnp(f"- Name: {org['name']}, ID: {org['id']} ")
        else:
            lm.lnp("No organizations found or unable to list organizations.", style="error")

    def get_org_detail(self, org_id: str):
        """
        This method gets detailed information for a specific organization.
        It takes an organization ID as a parameter.
        """
        org_details = self.dashboard.organizations.getOrganization(org_id)
        lm.print_inspect_info(org_details)
        if org_details is None:
            lm.lnp(f"Failed to get organization details for org_id: {org_id}")
        return org_details

    @staticmethod
    def select_organization(orgs):
        """
        Prompts the user to select an organization from the given list.
        """
        org_names = [org["name"] for org in orgs]  # Extract org names for user selection

        lm.lnp("Available organizations:")
        for i, org in enumerate(orgs, start=1):
            lm.lnp(f"{i}. {org['name']}, ID: {org['id']}")
        lm.lnp("[bold red]\nNote: Meraki organization names are case sensitive")
        while True:
            selection = Prompt.ask("Which organization should we use? Enter the number or name")
            if selection.isdigit() and 1 <= int(selection) <= len(orgs):
                return orgs[int(selection) - 1]["id"], orgs[int(selection) - 1]["name"]
            elif selection in org_names:
                for org in orgs:
                    if org["name"] == selection:
                        return org["id"], org["name"]
            lm.lnp(f"Invalid selection '{selection}'. Please try again.", level="error", style="error")

    @staticmethod
    def select_network(networks):
        """
        Prompts the user to select a network from the given list.
        """
        network_names = [network["name"] for network in networks]  # Extract network names for user selection

        lm.lnp("Available networks:")
        for i, network in enumerate(networks, start=1):
            lm.lnp(f"{i}. {network['name']}, ID: {network['id']}")
        while True:
            selection = Prompt.ask("Which network should we use? Enter the number or name")
            if selection.isdigit() and 1 <= int(selection) <= len(networks):  # If the selection is a number
                network_id = networks[int(selection) - 1]["id"]
                network_name = networks[int(selection) - 1]["name"]
                return network_id, network_name  # Return the network ID and name
            elif selection in network_names:
                for network in networks:
                    if network["name"] == selection:
                        return network["id"], network["name"]
            lm.lnp(f"Invalid selection '{selection}'. Please try again.", level="error", style="error")

    def get_org_id(self):
        """
        Fetches the organization ID based on the organization name, or prompts the user to select an organization if the name is left blank or is invalid.
        If there is only one organization, it selects that organization automatically.
        It exits the script if the organization is not found or if there's an error fetching the organizations.
        """
        orgs = self.get_orgs()
        if len(orgs) == 1:  # If one org, return early
            lm.lnp(f"Working with Org: {orgs[0]['name']}\n")
            org_id = orgs[0]["id"]
            org_name = orgs[0]["name"]
            return org_id, org_name
        else:
            org_id, org_name = self.select_organization(orgs)
            if org_name is None:
                lm.lnp(f"Organization with id '{org_id}' not found.", level="error", style="error")
                exit(1)
            return org_id, org_name

    def get_org_id_og(self):
        """
        This method fetches the organization ID based on the organization name, or prompts the user to select an organization if the name is left blank or is invalid.
        If there is only one organization, it selects that organization automatically.
        It exits the script if the organization is not found or if there's an error fetching the organizations.
        """
        orgs = self.get_orgs()

        lm.lnp(f"Found {len(orgs)} organization(s).")

        if len(orgs) == 1:  # If one org, return early
            lm.lnp(f"Working with Org: {orgs[0]['name']}\n")
            return orgs[0]["id"]
        org_names = [org["name"] for org in orgs]  # Extract org names for user selection
        lm.lnp("Available organizations:")
        for org in orgs:
            lm.lnp(f"- {org['name']}")
        lm.lnp("[bold red]\nNote: Meraki organization names are case sensitive")
        selection = Prompt.ask(
            "Which organization should we use?", choices=org_names, show_choices=False
        )
        organization_name = selection  # Update organization_name with the user's selection

        for org in orgs:
            if org["name"] == organization_name:
                return org["id"]

        lm.lnp(f"Organization with name '{organization_name}' not found.", level="error", style="error")
        exit(1)

    def get_networks(self, org_id: str):
        """
        This method collects existing Meraki network names / IDs for a specific organization.
        It takes an organization ID as a parameter.
        """
        networks = self.dashboard.organizations.getOrganizationNetworks(organizationId=org_id)
        return networks

    def list_networks(self, org_id: str):
        """
        This method fetches and prints all networks within a specified Meraki organization.
        It takes an organization ID as a parameter.
        """
        networks = self.get_networks(org_id=org_id)
        if networks:
            lm.lnp(f"Networks in Organization ID {org_id}:")
            for network in networks:
                lm.lnp(f"- Name: {network['name']}, ID: {network['id']} ")
        else:
            lm.lnp(f"No networks found or unable to list networks for organization ID {org_id}.", style="error")

    def get_org_config_changes(self, org_id: str, network_id: str, t0: int = None, t1: int = None, timespan: int = None):
        """
        This method gets the switch configuration for a specific organization and network within a specified timespan.
        It takes an organization ID, a network ID, and optional parameters for the start and end of the timespan.
        """
        # Prepare the query parameters
        params = {
            'networkId': network_id,
            't0': t0,
            't1': t1,
            'timespan': timespan
        }
        # Remove None values from the params dictionary
        params = {k: v for k, v in params.items() if v is not None}
        response = self.dashboard.organizations.getOrganizationConfigurationChanges(
            org_id,
            total_pages=3,
            **params  # Pass the query parameters
        )
        return response

    def fetch_config_changes(self, org_id: str, network_id: str, timespan: int, t0: int = None, t1: int = None):
        """
        This method fetches configuration changes for a specific organization and network within a specified timespan.
        """
        lm.lnp(f"\nFetching configuration changes for network ID {network_id} in organization ID {org_id}...")
        try:
            config_changes = self.get_org_config_changes(org_id=org_id, network_id=network_id, timespan=timespan, t0=t0, t1=t1)  # Get the configuration changes
        except Exception as e:
            lm.lnp(f"Error fetching configuration changes: {e}", style="error")
            return None

        if config_changes:
            lm.lnp(f"\nConfiguration changes found for network ID {network_id} in organization ID {org_id}")
        else:
            lm.lnp(f"\nNo configuration changes found for network ID {network_id} in organization ID {org_id}.", style="error")

        return config_changes

    def create_organization(self, org_name: str):
        """
        This method creates a new organization with the given name.
        It takes an organization name as a parameter.
        """
        try:
            new_org = self.dashboard.organizations.createOrganization(name=org_name)
            lm.lnp(f"New organization created successfully: {new_org}")
        except APIError as e:
            lm.lnp(f"API error creating new organization. Error: {str(e)}", style="error")
        except Exception as e:
            lm.lnp(f"Error creating new organization. Error: {str(e)}", style="error")

    def create_network(self, org_id: str, network_name: str, network_type: str):
        """
        This method creates a new network within a specified organization.
        It takes an organization ID, a network name, and a network type (wireless, appliance, switch, camera) as parameters.
        """
        try:
            new_network = self.dashboard.organizations.createOrganizationNetwork(
                organizationId=org_id,
                name=network_name,
                type=network_type
            )
            lm.lnp(f"New network created successfully: {new_network}")
            return new_network
        except APIError as e:
            lm.lnp(f"API error creating new network. Error: {str(e)}", style="error")
        except Exception as e:
            lm.lnp(f"Error creating new network. Error: {str(e)}", style="error")
