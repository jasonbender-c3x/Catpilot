from catpilot.tools.lib.catpilotcontainers import CatpilotCIContainer

def get_url(*args, **kwargs):
  return CatpilotCIContainer.get_url(*args, **kwargs)

def upload_file(*args, **kwargs):
  return CatpilotCIContainer.upload_file(*args, **kwargs)

def upload_bytes(*args, **kwargs):
  return CatpilotCIContainer.upload_bytes(*args, **kwargs)

BASE_URL = CatpilotCIContainer.BASE_URL
