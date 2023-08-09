create table public.service_types
(
    service_id        serial
        constraint service_types_pk
            primary key,
    service_name      varchar,
    is_deleted        integer,
    ip_id             integer,
    o_id              integer,
    git_url           varchar,
    service_file_name varchar,
    deploye_type      integer,
    created_time      timestamp,
    updated_time      timestamp
);

alter table public.service_types
    owner to postgres;

create table public.main_services
(
    main_service_id          serial
        constraint main_services_pk
            primary key,
    main_service_name        varchar,
    docker_compose_file_name varchar,
    service_id               integer
);

alter table public.main_services
    owner to postgres;

create table public.organization
(
    o_id         serial
        constraint organization_pk
            primary key,
    o_name       varchar,
    is_deleted   integer,
    created_time timestamp,
    updated_time timestamp
);

alter table public.organization
    owner to postgres;

create table public.gateway_setup_schema
(
    ip_id        integer default nextval('"gateway_Setup_schema_ip_id_seq"'::regclass) not null
        primary key,
    ip           varchar,
    is_deleted   integer,
    is_active    integer,
    created_time timestamp,
    updated_time timestamp,
    flag         integer,
    o_id         integer,
    username     varchar,
    password     varchar,
    panel_id     integer
);

alter table public.gateway_setup_schema
    owner to postgres;

create table public.errors
(
    flag_id       serial
        constraint errors_pk
            primary key,
    error_name    varchar,
    function_name varchar,
    created_time  varchar,
    updated_time  timestamp
);

alter table public.errors
    owner to postgres;

create table public.deployement_types
(
    deploye_type_id   integer not null
        constraint deployement_types_pk
            primary key,
    deploye_type_name varchar,
    is_deleted        integer,
    created_time      timestamp,
    updated_time      timestamp
);

alter table public.deployement_types
    owner to postgres;

create table public.requirement_variables
(
    req_v_id      serial
        constraint requirement_variables_pk
            primary key,
    variable_name varchar,
    value         varchar,
    is_deleted    integer,
    created_time  timestamp,
    updated_time  timestamp,
    ip_id         integer
);

alter table public.requirement_variables
    owner to postgres;

