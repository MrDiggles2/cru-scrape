from typing import List, Optional
import psycopg2
import os
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv
from src.entities import Site, PageItem, StartPage
from src.waybackurl import WaybackUrl

load_dotenv()

shared_connection = None

def get_connection():
  global shared_connection

  if shared_connection is None or shared_connection.closed != 0:
    shared_connection = psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port='5432'
    )

  return shared_connection

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
  with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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

def get_inprogress_pages(conn, site: Site, year: str):
  with conn.cursor(cursor_factory=RealDictCursor) as cursor:
    sql = """
      SELECT id, wb_url
      FROM public.pages
      WHERE
        site_id = %s
        AND year = %s
        AND content IS NULL
        AND error IS NULL
    """

    cursor.execute(sql, (site.id, year,))
    records = cursor.fetchall()

    return list(map(lambda record: StartPage(record), records))

def provision_empty_page(conn, site: Site, wb_url: WaybackUrl) -> Optional[str]:
  with conn.cursor() as cursor:
    sql = """
      INSERT INTO public.pages
        ( year, original_url, wb_url, content, original_timestamp, site_id )
      VALUES (%s, %s, %s, %s, %s, %s)
      ON CONFLICT (year, original_url)
        DO UPDATE
          SET
            content = EXCLUDED.content,
            updated_at = now()
      RETURNING id
    """

    values = (
      wb_url.get_snapshot_date().year,
      wb_url.get_original_url(),
      wb_url.get_full_url(),
      None,
      wb_url.get_snapshot_date(),
      site.id
    )

    cursor.execute(sql, values)

    return cursor.fetchone()[0] if cursor.rowcount > 0 else None

def upsert_page(conn, page: PageItem) -> str:
  with conn.cursor() as cursor:
    if page['page_id'] is not None:
      sql = f"""
        UPDATE public.pages
        SET content = %s
        WHERE id = '{page['page_id']}'
        RETURNING id
      """
      values = (page['content'],)
    else:
      url = WaybackUrl.from_url(page['wb_url'])

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
      values = (
        url.get_snapshot_date().year,
        url.get_original_url(),
        url.get_full_url(),
        page['content'],
        url.get_snapshot_date(),
        page['site_id']
      )


    cursor.execute(sql, values)

    return cursor.fetchone()[0]

def record_failure_by_id(conn, page_id: str, error: str):
  with conn.cursor() as cursor:
    sql = """
      UPDATE public.pages
      SET error = %s, content = NULL
      WHERE id = %s
    """
    values = (error, page_id)
    cursor.execute(sql, values)

def record_failure_by_url(conn, url: str, error: str):
  with conn.cursor() as cursor:
    sql = """
      UPDATE public.pages
      SET error = %s, content = NULL
      WHERE original_url = %s
    """
    values = (error, url)
    cursor.execute(sql, values)

def already_visited(conn, original_url: str, year: str):
  with conn.cursor() as cursor:
    sql = """
      SELECT COUNT(*)
      FROM public.pages
      WHERE original_url = %s and year = %s
    """

    row = select_first(cursor, sql, (original_url, year,))

    return True if row[0] > 0 else False

def get_all_sites(conn):
  with conn.cursor(cursor_factory=RealDictCursor) as cursor:
    sql = """
      SELECT
        id,
        start_url,
        base_url,
        organization_id,
        start_year,
        end_year
      from public.sites
    """

    cursor.execute(sql)
    records = cursor.fetchall()

    return list(map(lambda record: Site(record), records))
