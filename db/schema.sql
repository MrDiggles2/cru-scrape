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

GRANT ALL ON TABLE public.organizations TO postgres;

-- Index: name_department_uk

-- DROP INDEX IF EXISTS public.name_department_uk;

CREATE UNIQUE INDEX IF NOT EXISTS name_department_uk
    ON public.organizations USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST, COALESCE(department, 'unique_null_value'::text) COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Index: name_department_uk_test

-- DROP INDEX IF EXISTS public.name_department_uk_test;

CREATE UNIQUE INDEX IF NOT EXISTS name_department_uk_test
    ON public.organizations USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST, (department IS NULL) ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE department IS NULL;

-- Table: public.organization_aliases

-- DROP TABLE IF EXISTS public.organization_aliases;

CREATE TABLE IF NOT EXISTS public.organization_aliases
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name text COLLATE pg_catalog."default",
    department text COLLATE pg_catalog."default",
    organization_id uuid NOT NULL,
    CONSTRAINT organization_aliases_pkey PRIMARY KEY (id),
    CONSTRAINT organization_id_fk FOREIGN KEY (organization_id)
        REFERENCES public.organizations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.organization_aliases
    OWNER to postgres;

-- Table: public.sites

-- DROP TABLE IF EXISTS public.sites;

CREATE TABLE IF NOT EXISTS public.sites
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    start_url text COLLATE pg_catalog."default" NOT NULL,
    base_url text COLLATE pg_catalog."default" NOT NULL,
    organization_id uuid NOT NULL,
    start_year integer NOT NULL,
    end_year integer NOT NULL,
    CONSTRAINT sites_pkey PRIMARY KEY (id),
    CONSTRAINT url_uk UNIQUE (start_url),
    CONSTRAINT organization_id_fk FOREIGN KEY (organization_id)
        REFERENCES public.organizations (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.sites
    OWNER to postgres;

GRANT ALL ON TABLE public.sites TO postgres;

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

GRANT ALL ON TABLE public.pages TO postgres;