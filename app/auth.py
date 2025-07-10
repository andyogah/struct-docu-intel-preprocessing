
"""
Module: auth.py

This module provides various authentication methods for Azure services.
It includes authenticators for Managed Identity, Environment Variables, and Azure CLI.
The AuthenticatorFactory class is used to create an authenticator based on the specified `
authentication type.

Classes:
- AzureAuthenticator: Abstract base class for Azure authentication.
- ManagedIdentityAuthenticator: Authenticator for Managed Identity.
- EnvironmentVariableAuthenticator: Authenticator for Environment Variables.
- AzureCLIAuthenticator: Authenticator for Azure CLI.
- AuthenticatorFactory: Factory class to create an authenticator based on the specified `
  authentication type.
"""


from abc import ABC, abstractmethod
from azure.identity import DefaultAzureCredential, EnvironmentCredential, AzureCliCredential

class AzureAuthenticator(ABC):
    """
    Abstract base class for Azure authentication.
    """
    @abstractmethod
    def get_credential(self):
        """
        Abstract method to get the Azure credential.
        """
        #pass

class ManagedIdentityAuthenticator(AzureAuthenticator):
    """
    Authenticator for Managed Identity.
    """
    def get_credential(self):
        """
        Get the Azure credential using Managed Identity.
        
        Returns:
            DefaultAzureCredential: The Azure credential.
        """
        return DefaultAzureCredential()

class EnvironmentVariableAuthenticator(AzureAuthenticator):
    """
    Authenticator for Environment Variables.
    """
    def get_credential(self):
        """
        Get the Azure credential using environment variables.
        
        Returns:
            EnvironmentCredential: The Azure credential.
        """
        return EnvironmentCredential()

class AzureCLIAuthenticator(AzureAuthenticator):
    """
    Authenticator for Azure CLI.
    """
    def get_credential(self):
        """
        Get the Azure credential using Azure CLI.
        
        Returns:
            AzureCliCredential: The Azure credential.
        """
        return AzureCliCredential()

class AuthenticatorFactory:
    """
    Factory class to create an authenticator based on the specified authentication type.
    """
    def __init__(self, auth_type='managed_identity'):
        """
        Initialize the factory with the specified authentication type.
        
        Args:
            auth_type (str): The authentication type. Default is 'managed_identity'.
        """
        self.auth_type = auth_type

    def get_authenticator(self):
        """
        Get the authenticator based on the specified authentication type.
        
        Returns:
            AzureAuthenticator: The authenticator.
        """
        if self.auth_type == 'environment':
            return EnvironmentVariableAuthenticator()
        elif self.auth_type == 'azure_cli':
            return AzureCLIAuthenticator()
        else:
            return ManagedIdentityAuthenticator()
