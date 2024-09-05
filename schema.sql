-- Table: public.organizations

-- DROP TABLE IF EXISTS public.organizations;

CREATE TABLE IF NOT EXISTS public.organizations
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name text COLLATE pg_catalog."default" NOT NULL,
    department text COLLATE pg_catalog."default",
    type text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT organizations_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.organizations
    OWNER to postgres;

REVOKE ALL ON TABLE public.organizations FROM scrape_ro;

GRANT ALL ON TABLE public.organizations TO postgres;

GRANT SELECT ON TABLE public.organizations TO scrape_ro;

-- Table: public.sites

-- DROP TABLE IF EXISTS public.sites;

CREATE TABLE IF NOT EXISTS public.sites
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    url text COLLATE pg_catalog."default" NOT NULL,
    organization_id uuid NOT NULL,
    start_year integer NOT NULL,
    end_year integer NOT NULL,
    CONSTRAINT sites_pkey PRIMARY KEY (id),
    CONSTRAINT url_uk UNIQUE (url),
    CONSTRAINT organization_id_fk FOREIGN KEY (organization_id)
        REFERENCES public.organizations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.sites
    OWNER to postgres;

REVOKE ALL ON TABLE public.sites FROM scrape_ro;

GRANT ALL ON TABLE public.sites TO postgres;

GRANT SELECT ON TABLE public.sites TO scrape_ro;

-- Table: public.pages

-- DROP TABLE IF EXISTS public.pages;

CREATE TABLE IF NOT EXISTS public.pages
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    year integer NOT NULL,
    original_url text COLLATE pg_catalog."default" NOT NULL,
    wb_url text COLLATE pg_catalog."default" NOT NULL,
    content text COLLATE pg_catalog."default" NOT NULL,
    original_timestamp timestamp with time zone NOT NULL DEFAULT now(),
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    site_id uuid NOT NULL,
    CONSTRAINT pages_pkey PRIMARY KEY (id),
    CONSTRAINT year_url_uk UNIQUE (year, original_url),
    CONSTRAINT site_id_fk FOREIGN KEY (site_id)
        REFERENCES public.sites (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pages
    OWNER to postgres;

REVOKE ALL ON TABLE public.pages FROM scrape_ro;

GRANT ALL ON TABLE public.pages TO postgres;

GRANT SELECT ON TABLE public.pages TO scrape_ro;