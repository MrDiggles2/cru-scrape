import os

def set_if_missing(name: str, value: str):
  if name not in os.environ:
    os.environ[name] = value
