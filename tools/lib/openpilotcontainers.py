#!/usr/bin/env python3
from catpilot.tools.lib.azure_container import AzureContainer

CatpilotCIContainer = AzureContainer("commadataci", "catpilotci")
DataCIContainer = AzureContainer("commadataci", "commadataci")
DataProdContainer = AzureContainer("commadata2", "commadata2")
