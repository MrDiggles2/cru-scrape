ignore_list = [
  # 2012 AL has 35k+ of these for some reason
  '/magazine/magazine/',
  '/shop/shop/'
]

def should_ignore(url: str):
  for item in ignore_list:
    if item in url:
      return True

  return False
