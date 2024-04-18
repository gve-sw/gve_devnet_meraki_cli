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

from app.logger.logrr import lm
from typing import Optional, Tuple
from app.meraki_api.meraki import MerakiOps
import meraki


class Validators:
    """
    Validators class to validate API keys and tokens.
    """

    @staticmethod
    def validate_some_var(some_var: Optional[str]) -> bool:
        """
        Template - Validate some_var.
        """
        print(f"Validating some_var: {some_var}")
        return isinstance(some_var, str) and len(some_var) > 0

    @staticmethod
    def validate_meraki_api_key(api_key: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """Validate Meraki API Key."""
        # Check if the API key meets the length and alphanumeric requirements
        if not (20 <= len(api_key) <= 128 and api_key.isalnum()):
            return False, "Invalid API Key: Must be alphanumeric and between 20 to 128 characters long.", None, None

        # Try to instantiate the Meraki Dashboard with the API key
        try:
            meraki_ops = MerakiOps(api_key=api_key)  # Instantiate the MerakiOps class
            meraki_ops = meraki_ops.get_instance()  # Get the instance of the MerakiOps class
            try:
                orgs = meraki_ops.get_orgs()  # Get the organizations
                if orgs:
                    return True, "Meraki API Key is valid.", orgs[0]['id'], orgs[0]['name']  # Return the organization ID and name
                else:
                    return False, "No organizations found with the provided API key.", None, None  # No organizations found
            except meraki.APIError as e:
                return False, f"API Error: {e}", None, None
        except Exception as e:
            lm.lnp(f"Error validating Meraki API Key: {str(e)}", style="error", level="error")
            return False, "Error validating Meraki API Key.", None, None


vd = Validators()
