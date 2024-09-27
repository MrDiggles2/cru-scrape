from src.utils.psql import get_connection, get_all_sites

def list_combos():
  with get_connection() as conn:
    sites = get_all_sites(conn)

    for site in sites:
      for year in range(site.start_year, site.end_year + 1):
        if year % 4 == 0:
          print(f'{year} {site.id}')
