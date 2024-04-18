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

from dotenv import load_dotenv, set_key
import os
from pathlib import Path
import typer
from app.logger.logrr import lm
from app.config.config import c
from typing import ClassVar, Optional, Union, List
from app.env_manager.vd import vd
from app.meraki_api.meraki import MerakiOps

ENV_FILE_PATH = c.ENV_FILE_PATH


class EM:
    """
    Environment Manager class to manage environment variables and configuration.
    """
    _instance: ClassVar[Optional['EM']] = None

    def __init__(self, env_path: Path):
        """
        Initialize the Environment Manager with the path to the .env file.
        """
        self.env_path = Path(env_path)  # Convert the env_path to a pathlib.Path object
        self.validator = vd  # Validator instance
        self.vars_and_validators = {
            'MERAKI_API_KEY': vd.validate_meraki_api_key
        }

    @classmethod
    def get_instance(cls) -> 'EM':
        """
        Returns a singleton instance of Environment Manager.
        """
        if cls._instance is None:
            cls._instance = cls(env_path=c.ENV_FILE_PATH)
        return cls._instance

    def create_and_load_env_if_missing(self):
        """
        Create the .env file if it doesn't exist and load the environment variables from it.
        """
        # lm.lnp(self.env_path)   # Print the path to the .env file
        if not self.env_path.exists():
            self.env_path.touch()
        load_dotenv(dotenv_path=self.env_path)

    def reload_env(self):
        """
        Reload the environment variables from the .env file.
        """
        load_dotenv(dotenv_path=self.env_path)

    def set_env_var(self, var_name: str, var_value: str, callback=None):
        """
        Set an environment variable and update the .env file.
        """
        os.environ[var_name] = var_value    # Set the environment variable
        set_key(self.env_path.as_posix(), var_name, var_value, quote_mode="never")  # Update the .env file
        load_dotenv(dotenv_path=self.env_path)
        if callback:
            callback()  # Reload configuration after setting
        lm.lnp(f"{var_name} is set and valid.", style="success")

    def ensure_env_set(self, var_name: str, prompt_message: str, validation_func=lambda x: True, callback=None):
        """
        Ensure that a specified environment variable is set and valid.
        If the variable is not set or invalid, prompt the user to enter a valid value.
        """
        while True:
            var_name = var_name.upper()  # Convert to uppercase as a common convention
            var_value = os.getenv(var_name)  # Check if the variable is already set
            if not var_value or not validation_func(var_value):  # If the variable is not set or invalid
                var_value = typer.prompt(prompt_message)  # Prompt the user for the variable value
                if validation_func(var_value):  # Validate the user input
                    self.set_env_var(var_name, var_value, callback=callback)
                    break
                else:
                    lm.lnp(f"Invalid value for {var_name}. Please try again.", style="error")
            else:
                lm.lnp(f"{var_name} is already set and valid.", style="success")
                break

    def ensure_vars_set(self, var_names: Union[str, List[str]], callback=None):
        """
        Ensure that the specified environment variables are set and valid, given a single variable name or a list of names.

        Args:
            var_names (Union[str, List[str]]): Single variable name or a list of variable names.
            callback (function, optional): Callback function to be executed after setting the environment variable. Defaults to None.
        """
        if isinstance(var_names, str):
            var_names = [var_names]  # Convert a single variable name into a list

        for var_name in var_names:
            if var_name in self.vars_and_validators:
                validation_func = self.vars_and_validators[var_name]
                prompt_message = f"{var_name} is not set. Please enter it"
                self.ensure_env_set(var_name, prompt_message, validation_func, callback)

    def set_meraki_api_key(self, api_key: Optional[str] = None) -> tuple:
        """
        Set the Meraki API key as an environment variable.
        """
        if api_key:
            meraki_ops = MerakiOps(api_key=api_key)
            org_id, org_name = meraki_ops.get_org_id()
            org_name = org_name.replace(" ", "_")  # Replace spaces with underscores
            new_api_key = f"MERAKI_API_KEY_{org_name}"
            is_valid, message, _, _ = vd.validate_meraki_api_key(api_key=api_key)  # Validate the API key
            if is_valid:
                self.set_env_var(var_name=new_api_key, var_value=api_key)
                return is_valid, message, org_id, org_name
            else:
                print(message)  # Print the validation message
            return is_valid, message, None, None
        else:
            return False, "API key is not provided.", None, None


em = EM.get_instance()
