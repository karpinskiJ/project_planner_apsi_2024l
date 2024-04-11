CREATE DATABASE project_planner;
\c project_planner;


CREATE TABLE projects(
    id serial NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT pk_projects PRIMARY KEY (id)
);


CREATE TABLE users
(
 id        serial NOT NULL,
 login     varchar(50) NOT NULL,
 password  varchar(50) NOT NULL,
 name      varchar(50) NOT NULL,
 surname  varchar(50) NOT NULL,
 role     varchar(50) NOT NULL,
 project_id integer NOT NULL,
 CONSTRAINT pk_users PRIMARY KEY ( "id" ),
 CONSTRAINT fk_users_projects FOREIGN KEY ( project_id ) REFERENCES projects ( "id" )
);

CREATE TABLE technical_resources(
    id serial  NOT NULL,
    name VARCHAR(100) NOT NULL,
    project_id integer NOT NULL,
    CONSTRAINT pk_technical_resources PRIMARY KEY (id),
    CONSTRAINT fk_technical_resources_projects FOREIGN KEY ( project_id ) REFERENCES projects ( "id" )
);

INSERT INTO projects (name, description, start_date, end_date, status)
VALUES
('Project A', 'Description of Project A', '2024-01-01', '2024-06-30', 'In Progress'),
('Project B', 'Description of Project B', '2024-02-15', '2024-08-31', 'Pending'),
('Project C', 'Description of Project C', '2024-03-20', '2024-07-15', 'Completed');


INSERT INTO users (login, password, name, surname, role, project_id)
VALUES
('user1', 'password1', 'John', 'Doe', 'Developer', 1),
('user2', 'password2', 'Jane', 'Smith', 'Project Manager', 2),
('user3', 'password3', 'Michael', 'Johnson', 'Tester', 3),
('user4', 'password4', 'Emily', 'Brown', 'Designer', 1),
('user5', 'password5', 'David', 'Wilson', 'Developer', 2);


INSERT INTO technical_resources (name, project_id)
VALUES
('Resource 1', 1),
('Resource 2', 2),
('Resource 3', 3),
('Resource 4', 1),
('Resource 5', 2);