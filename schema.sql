-- Table: public.scrape_results

-- DROP TABLE IF EXISTS public.scrape_results;

CREATE TABLE IF NOT EXISTS public.scrape_results
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    year integer NOT NULL,
    base_url character varying COLLATE pg_catalog."default" NOT NULL,
    original_url text COLLATE pg_catalog."default" NOT NULL,
    wb_url text COLLATE pg_catalog."default" NOT NULL,
    content text COLLATE pg_catalog."default" NOT NULL,
    original_timestamp timestamp with time zone,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT scrape_results_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.scrape_results
    OWNER to postgres;

REVOKE ALL ON TABLE public.scrape_results FROM scrape_ro;

GRANT ALL ON TABLE public.scrape_results TO postgres;

GRANT SELECT ON TABLE public.scrape_results TO scrape_ro;