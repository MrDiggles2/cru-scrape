
def select_first(cursor, query, vars):
  cursor.execute(query, vars)
  records = cursor.fetchall()
  return records[0] if cursor.rowcount > 0 else None

def get_organization_id(cursor, name, department, type):
  sql = """
    SELECT id
    FROM public.organizations
    WHERE name = %s AND department = %s AND type = %s
  """
  row = select_first(cursor, sql, (name, department, type))

  return row[0] if row != None else None

def organization_alias_exists(cursor, current_org_id, name, department):
  sql = """
    SELECT count(*)
    FROM public.organization_aliases
    WHERE name = %s AND department = %s AND organization_id = %s
  """
  row = select_first(cursor, sql, (name, department, current_org_id))

  return True if row[0] > 0 else False

def insert_organization(cursor, name: str, department: str, type: str):
  sql = """
    INSERT INTO public.organizations (name, department, type)
      VALUES (%s, %s, %s)
    RETURNING id
  """

  cursor.execute(sql, (name, department, type))
  return cursor.fetchone()[0]

def insert_organization_alias(cursor, current_org_id, name, department):
  sql = """
    INSERT INTO public.organization_aliases (organization_id, name, department)
      VALUES (%s, %s, %s)
  """

  cursor.execute(sql, (current_org_id, name, department))

def site_exists(cursor, site_url, current_org_id):
  sql = """
    SELECT count(*)
    FROM public.sites
    WHERE url = %s AND organization_id = %s
  """
  row = select_first(cursor, sql, (site_url, current_org_id))

  return True if row[0] > 0 else False

def insert_site(cursor, site_url, current_org_id, start_year, end_year):
  sql = """
    INSERT INTO public.sites (url, organization_id, start_year, end_year)
      VALUES (%s, %s, %s, %s)
  """

  cursor.execute(sql, (site_url, current_org_id, start_year, end_year))