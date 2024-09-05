REVOKE ALL ON TABLE public.organizations FROM scrape_ro;
GRANT SELECT ON TABLE public.organizations TO scrape_ro;

REVOKE ALL ON TABLE public.sites FROM scrape_ro;
GRANT SELECT ON TABLE public.sites TO scrape_ro;

REVOKE ALL ON TABLE public.pages FROM scrape_ro;
GRANT SELECT ON TABLE public.pages TO scrape_ro;