from typing import List
import psycopg2
import os
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv
from src.entities import Site, PageItem
from src.waybackurl import WaybackUrl

load_dotenv()

def get_connection():
  return psycopg2.connect(
      database=os.getenv('DB_NAME'),
      user=os.getenv('DB_USER'),
      password=os.getenv('DB_PASSWORD'),
      host=os.getenv('DB_HOST'),
      port='5432'
  )

def select_first(cursor, query, vars):
  cursor.execute(query, vars)
  records = cursor.fetchall()
  return records[0] if cursor.rowcount > 0 else None

def get_organization_id(cursor, name, department, type):
  sql = """
    SELECT id
    FROM public.organizations
    WHERE name = %s AND (department = %s OR department is NULL) AND type = %s
  """
  row = select_first(cursor, sql, (name, department, type))

  return row[0] if row != None else None

def organization_alias_exists(cursor, current_org_id, name, department):
  sql = """
    SELECT count(*)
    FROM public.organization_aliases
    WHERE name = %s AND (department = %s OR department is NULL) AND organization_id = %s
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
    WHERE start_url = %s AND organization_id = %s
  """
  row = select_first(cursor, sql, (site_url, current_org_id))

  return True if row[0] > 0 else False

def insert_site(cursor, site_url, base_url, current_org_id, start_year, end_year):
  sql = """
    INSERT INTO public.sites (start_url, base_url, organization_id, start_year, end_year)
      VALUES (%s, %s, %s, %s, %s)
  """

  cursor.execute(sql, (site_url, base_url, current_org_id, start_year, end_year))

def get_site_by_id(conn, site_id):
  cursor = conn.cursor(cursor_factory=RealDictCursor)

  sql = """
    SELECT
      id,
      start_url,
      base_url,
      organization_id,
      start_year,
      end_year
    from public.sites
    where id = %s
  """

  cursor.execute(sql, (site_id,))
  return Site(cursor.fetchone()) if cursor.rowcount > 0 else None

def get_inprogress_pages(conn, site: Site, year: str) -> List[str]:
  cursor = conn.cursor()

  sql = """
    SELECT wb_url
    FROM public.pages
    WHERE
      site_id = %s
      AND year = %s
      AND content IS NULL
  """

  cursor.execute(sql, (site.id, year,))
  records = cursor.fetchall()

  return list(map(lambda record: record[0], records))

def provision_empty_pages(conn, site: Site, wb_urls: List[WaybackUrl]):
  cursor = conn.cursor()

  sql = """
    INSERT INTO public.pages
      ( year, original_url, wb_url, content, original_timestamp, site_id )
    VALUES %s
    ON CONFLICT (year, original_url)
      DO NOTHING
  """

  def getValues(wb_url: WaybackUrl):
    return (
      wb_url.get_snapshot_date().year,
      wb_url.get_original_url(),
      wb_url.get_full_url(),
      None,
      wb_url.get_snapshot_date(),
      site.id
    )

  data = list(map(getValues, wb_urls))
  execute_values(cursor, sql, data)
  conn.commit()

def upsert_page(conn, page: PageItem) -> str:
  cursor = conn.cursor()

  sql = """
    INSERT INTO public.pages
      ( year, original_url, wb_url, content, original_timestamp, site_id )
    VALUES
      ( %s, %s, %s, %s, %s, %s )
    ON CONFLICT (year, original_url)
      DO UPDATE
        SET
          content = EXCLUDED.content,
          original_timestamp = EXCLUDED.original_timestamp,
          updated_at = now()
    RETURNING id
  """

  url = WaybackUrl.from_url(page['wb_url'])

  cursor.execute(sql, (
    url.get_snapshot_date().year,
    url.get_original_url(),
    url.get_full_url(),
    page['content'],
    url.get_snapshot_date(),
    page['site_id']
  ))

  return cursor.fetchone()[0]