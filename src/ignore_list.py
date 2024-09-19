ignore_list = [
  # 2012 has 35k+ of these for some reason
  'https://www.outdooralabama.com/magazine/magazine'
]

def should_ignore(url: str):
  for item in ignore_list:
    if item in url:
      return True

  return False
