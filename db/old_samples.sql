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
