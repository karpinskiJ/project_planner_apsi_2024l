CREATE DATABASE project_planner;
\c project_planner;


CREATE TABLE projects(
    id serial NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    owner_id integer NOT NULL,
    CONSTRAINT pk_projects PRIMARY KEY (id)
    --CONSTRAINT fk_owner FOREIGN KEY ( owner_id ) REFERENCES users ( "id" )
);


CREATE TABLE users(
	id        serial NOT NULL,
	login     varchar(50) NOT NULL,
	password  varchar(200) NOT NULL,
	name      varchar(50) NOT NULL,
	surname  varchar(50) NOT NULL,
	role     varchar(50) NOT NULL,
	project_id integer,
	setup_time timestamp NOT NULL,
	CONSTRAINT pk_users PRIMARY KEY ( "id" ),
	CONSTRAINT fk_users_projects FOREIGN KEY ( project_id ) REFERENCES projects ( "id" )
);

CREATE TABLE technical_resources(
    id serial  NOT NULL,
    name VARCHAR(100) NOT NULL,
    project_id integer,
    CONSTRAINT pk_technical_resources PRIMARY KEY (id),
    CONSTRAINT fk_technical_resources_projects FOREIGN KEY ( project_id ) REFERENCES projects ( "id" )
);

CREATE TABLE system_admins(
	id integer NOT NULL,
	parent_id integer,
	promotion_time timestamp NOT NULL,
	CONSTRAINT pk_admins PRIMARY KEY (id),
	CONSTRAINT fk_admins_users FOREIGN KEY (id) REFERENCES users ( "id" ),
	CONSTRAINT fk_admins_super_users FOREIGN KEY (parent_id) REFERENCES users ( "id" )
);
