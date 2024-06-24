CREATE DATABASE project_planner;
\c project_planner;

CREATE TYPE project_role AS ENUM ('manager', 'worker', 'admin');
CREATE TABLE users(
	id        serial NOT NULL,
	login     varchar(50) NOT NULL,
	password  varchar(200) NOT NULL,
	name      varchar(50) NOT NULL,
	surname  varchar(50) NOT NULL,
	role     project_role NOT NULL,
	setup_time timestamp NOT NULL,
	CONSTRAINT pk_users PRIMARY KEY ( "id" )
);
INSERT INTO users (login, password, name, surname, role, setup_time) VALUES
('manager1', '$2b$12$HDuQW0Vp97aVjBY4LBgltO2Hn6sPKtyw92A2BoNzStEjolgr6SwLm', 'John', 'Doe', 'manager', NOW()),
('worker1', '$2b$12$HDuQW0Vp97aVjBY4LBgltO2Hn6sPKtyw92A2BoNzStEjolgr6SwLm', 'Jane', 'Smith', 'worker', NOW()),
('worker2', '$2b$12$HDuQW0Vp97aVjBY4LBgltO2Hn6sPKtyw92A2BoNzStEjolgr6SwLm', 'Emily', 'Johnson', 'worker', NOW()),
('admin1', '$2b$12$HDuQW0Vp97aVjBY4LBgltO2Hn6sPKtyw92A2BoNzStEjolgr6SwLm', 'Alice', 'Williams', 'admin', NOW()),
('manager2', '$2b$12$HDuQW0Vp97aVjBY4LBgltO2Hn6sPKtyw92A2BoNzStEjolgr6SwLm', 'Robert', 'Brown', 'manager', NOW()),
('worker3', '$2b$12$HDuQW0Vp97aVjBY4LBgltO2Hn6sPKtyw92A2BoNzStEjolgr6SwLm', 'Michael', 'Davis', 'worker', NOW()),

CREATE TYPE project_status AS ENUM ('pending', 'in_progress','completed');
CREATE TABLE projects(
    id serial NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status project_status NOT NULL,
    owner_id integer NOT NULL,
    CONSTRAINT pk_projects PRIMARY KEY (id),
    CONSTRAINT fk_owner FOREIGN KEY ( owner_id ) REFERENCES users ( "id" )
);

--INIT DATA
INSERT INTO projects (name, description, start_date, end_date, status,owner_id)
VALUES
('Project A', 'Description of Project A', '2024-06-01', '2024-06-30', 'in_progress',1),
('Project B', 'Description of Project B', '2024-06-15', '2024-08-31', 'pending',1),
('Project C', 'Description of Project C', '2024-03-20', '2024-06-01', 'completed',5);

CREATE TYPE resource_type as ENUM('it_equipment','vehicle','office_equipment','other');
CREATE TABLE technical_resources(
    id serial  NOT NULL,
    name VARCHAR(100) NOT NULL,
    owner_id integer,
    type resource_type NOT NULL,
    CONSTRAINT pk_technical_resources PRIMARY KEY (id)                 ,
    CONSTRAINT fk_user_id FOREIGN KEY (owner_id) REFERENCES users ("id")
);
INSERT INTO technical_resources (name,onwer_id,type) VALUES
 ('car',1,'vehicle'),
 ('laptop',1,'it_equipment'),
 ('screen',1,'it_equipment'),
 ('printer',1,'it_equipment'),
 ('desk',1,'office_equipment'),
 ('chair',1,'office_equipment'),
 ('table',5,'office_equipment'),
 ('phone',1,'office_equipment'),
 ('other',5,'other') ;

create table projects_to_resources_lkp(
    id serial NOT NULL,
    project_id integer NOT NULL,
    user_id integer,
    resource_id integer,
    allocation_part decimal  ,
     CONSTRAINT pk_projects_to_members PRIMARY KEY ("id"),
     CONSTRAINT fk_project_id FOREIGN KEY (project_id) REFERENCES projects ("id"),
     CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users ("id"),
     CONSTRAINT fk_resource_id FOREIGN KEY (resource_id) REFERENCES technical_resources ("id")

);
-- Insert sample data into projects_to_resources_lkp table
INSERT INTO projects_to_resources_lkp (project_id, user_id, resource_id, allocation_part) VALUES
(1, 1, NULL, 1.0),
(1, 2, Null, 0.5),
(2, 2, Null, 0.5),
(2, 5, Null, 0.5),
(2, 3, Null, 0.6),
(1,NULL,1,0.6),
(2,NULL,1,0.4),
(1,NULL,2,1.0),
(1,NULL,3,1.0);







