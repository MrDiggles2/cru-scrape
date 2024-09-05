import os
import pandas as pd
import psycopg2
import os
import numpy as np
from dotenv import load_dotenv
from src.utils.psql import insert_organization, insert_organization_alias, get_organization_id, organization_alias_exists, site_exists, insert_site
 
load_dotenv()

conn = psycopg2.connect(
    database="scrape_results",
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port='5432'
)

cursor = conn.cursor()

dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(dir_path, './modified.tsv');

df = pd.read_csv(file_path, sep="\t")
df = df.replace({np.nan: None})

current_org_id = None

for row_dict in df.to_dict(orient="records"):
  entry = row_dict['Entry']
  organization_name = row_dict['Organization']
  department = row_dict['Department']
  type = row_dict['Type']
  site_url = row_dict['Link']
  start_year = row_dict['Start Date']
  end_year = row_dict['End Date']

  # Create an organization if "entry" is 1

  if (entry == 1.0):
    existing_org_id = get_organization_id(cursor, organization_name, department, type)

    if (existing_org_id == None):
      current_org_id = insert_organization(cursor, organization_name, department, type)
      print("ORGANIZATION %s %s %s: inserted" % (organization_name, department, type))
    else:
      current_org_id = existing_org_id
      print("ORGANIZATION %s %s %s: skipped" % (organization_name, department, type))

  # Always insert the alias if not already in db

  if (organization_alias_exists(cursor, current_org_id, organization_name, department)):
    print("ALIAS %s %s %s: skipped" % (current_org_id, organization_name, department))
  else:
    insert_organization_alias(cursor, current_org_id, organization_name, department)
    print("ALIAS %s %s %s: inserted" % (current_org_id, organization_name, department))

  # Always insert site if not already in db

  if (site_exists(cursor, site_url, current_org_id)):
    print("SITE %s %s %s: inserted" % (current_org_id, organization_name, department))
  else:
    insert_site(cursor, site_url, current_org_id, start_year, end_year)
    print("SITE %s %s %s: inserted" % (current_org_id, organization_name, department))

conn.commit()
conn.close()


