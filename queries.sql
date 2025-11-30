create schema newKSU;
use newKSU;

create table buildings
(
    building varchar(20),
    primary key (building)
);

create table classroom
    (roomID numeric (6, 0) NOT NULL AUTO_INCREMENT,
     building        NOT NULL varchar(20),
     room_number       NOT NULL varchar(7),
     capacity        NOT NULL numeric(4,0),
     primary key (roomId),
     foreign key (building) references buildings (building)
    );

create table department
    (dept_name        varchar(20), 
     building        varchar(15), 
     budget                numeric(12,2) check (budget > 0),
     primary key (dept_name)
    );

create table course
    (course_id        varchar(8), 
     title            varchar(50), 
     dept_name        varchar(20),
     credits        numeric(2,0) check (credits > 0),
     primary key (course_id),
     foreign key (dept_name) references department (dept_name)
        on delete set null
    );

create table instructor
    (ID            varchar(5), 
     name            varchar(20) not null, 
     dept_name        varchar(20), 
     salary            numeric(8,2) check (salary > 29000),
     primary key (ID),
     foreign key (dept_name) references department (dept_name)
        on delete set null
    );

create table section
    (course_id        varchar(8), 
     sec_id            varchar(8),
     semester        varchar(6)
        check (semester in ('Fall', 'Winter', 'Spring', 'Summer')), 
     year            numeric(4,0) check (year > 1701 and year < 2100), 
     roomID        numeric(6, 0),
     time_slot_id        varchar(4),
     primary key (course_id, sec_id, semester, year),
     foreign key (course_id) references course (course_id)
        on delete cascade,
     foreign key (roomID) references classroom (roomID)
        on delete set null
    );

create table teaches
    (ID            varchar(5), 
     course_id        varchar(8),
     sec_id            varchar(8), 
     semester        varchar(6),
     year            numeric(4,0),
     primary key (ID, course_id, sec_id, semester, year),
     foreign key (course_id, sec_id, semester, year) references section (course_id, sec_id, semester, year)
        on delete cascade,
     foreign key (ID) references instructor (ID)
        on delete cascade
    );

create table student
    (stu_ID            varchar(5), 
     name            varchar(20) not null, 
     dept_name        varchar(20), 
     tot_cred        numeric(3,0) check (tot_cred >= 0),
     primary key (stu_ID),
     foreign key (dept_name) references department (dept_name)
        on delete set null
    );

create table takes
    (stu_ID            varchar(5), 
     course_id        varchar(8),
     sec_id            varchar(8), 
     semester        varchar(6),
     year            numeric(4,0),
     grade                varchar(2),
     primary key (stu_ID, course_id, sec_id, semester, year),
     foreign key (course_id, sec_id, semester, year) references section (course_id, sec_id, semester, year)
        on delete cascade,
     foreign key (stu_ID) references student (stu_ID)
        on delete cascade
    );

create table advisor
    (s_ID            varchar(5),
     i_ID            varchar(5),
     primary key (s_ID),
     foreign key (i_ID) references instructor (ID)
        on delete set null,
     foreign key (s_ID) references student (stu_ID)
        on delete cascade
    );

create table time_slot
    (time_slot_id        varchar(4),
     day            varchar(1),
     start_time TIME,
     end_time TIME,
     primary key (time_slot_id, day, start_time, end_time)
    );

create table prereq
    (course_id        varchar(8), 
     prereq_id        varchar(8),
     primary key (course_id, prereq_id),
     foreign key (course_id) references course (course_id)
        on delete cascade,
     foreign key (prereq_id) references course (course_id)
    );

CREATE TABLE IF NOT EXISTS `accounts` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `student_id` varchar(5),
    `instructor_id` varchar(5),
    `username` varchar(50) NOT NULL,
    `password` varchar(255) NOT NULL,
    `email` varchar(100) NOT NULL,
    `permissions` varchar(100) NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (student_id) REFERENCES student(stu_ID),
    FOREIGN KEY (instructor_id) REFERENCES instructor(ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


delete from prereq;
delete from time_slot;
delete from advisor;
delete from takes;
delete from student;
delete from teaches;
delete from section;
delete from instructor;
delete from course;
delete from department;
delete from classroom;
delete from buildings;
insert into buildings values ("Painter");
insert into buildings values ("Packard");
insert into buildings values ("Taylor");
insert into buildings values ("Watson");
insert into classroom values (1, 'Packard', '101', '500');
insert into classroom values (2, 'Painter', '514', '10');
insert into classroom values (3, 'Taylor', '3128', '70');
insert into classroom values (4, 'Watson', '100', '30');
insert into classroom values (5, 'Watson', '120', '50');
insert into department values ('Biology', 'Watson', '90000');
insert into department values ('Comp. Sci.', 'Taylor', '100000');
insert into department values ('Elec. Eng.', 'Taylor', '85000');
insert into department values ('Finance', 'Painter', '120000');
insert into department values ('History', 'Painter', '50000');
insert into department values ('Music', 'Packard', '80000');
insert into department values ('Physics', 'Watson', '70000');
insert into course values ('BIO-101', 'Intro. to Biology', 'Biology', '4');
insert into course values ('BIO-301', 'Genetics', 'Biology', '4');
insert into course values ('BIO-399', 'Computational Biology', 'Biology', '3');
insert into course values ('CS-101', 'Intro. to Computer Science', 'Comp. Sci.', '4');
insert into course values ('CS-190', 'Game Design', 'Comp. Sci.', '4');
insert into course values ('CS-315', 'Robotics', 'Comp. Sci.', '3');
insert into course values ('CS-319', 'Image Processing', 'Comp. Sci.', '3');
insert into course values ('CS-347', 'Database System Concepts', 'Comp. Sci.', '3');
insert into course values ('EE-181', 'Intro. to Digital Systems', 'Elec. Eng.', '3');
insert into course values ('FIN-201', 'Investment Banking', 'Finance', '3');
insert into course values ('HIS-351', 'World History', 'History', '3');
insert into course values ('MU-199', 'Music Video Production', 'Music', '3');
insert into course values ('PHY-101', 'Physical Principles', 'Physics', '4');
insert into instructor values ('10101', 'Srinivasan', 'Comp. Sci.', '65000');
insert into instructor values ('12121', 'Wu', 'Finance', '90000');
insert into instructor values ('15151', 'Mozart', 'Music', '40000');
insert into instructor values ('22222', 'Einstein', 'Physics', '95000');
insert into instructor values ('32343', 'El Said', 'History', '60000');
insert into instructor values ('33456', 'Gold', 'Physics', '87000');
insert into instructor values ('45565', 'Katz', 'Comp. Sci.', '75000');
insert into instructor values ('58583', 'Califieri', 'History', '62000');
insert into instructor values ('76543', 'Singh', 'Finance', '80000');
insert into instructor values ('76766', 'Crick', 'Biology', '72000');
insert into instructor values ('83821', 'Brandt', 'Comp. Sci.', '92000');
insert into instructor values ('98345', 'Kim', 'Elec. Eng.', '80000');
insert into section values ('BIO-101', '1', 'Summer', '2017', 2, 'B');
insert into section values ('BIO-301', '1', 'Summer', '2018', 2, 'A');
insert into section values ('CS-101', '1', 'Fall', '2017', 2, 'H');
insert into section values ('CS-101', '1', 'Spring', '2018', 2, 'F');
insert into section values ('CS-190', '1', 'Spring', '2017', 3, 'E');
insert into section values ('CS-190', '2', 'Spring', '2017', 3, 'A');
insert into section values ('CS-315', '1', 'Spring', '2018', 5, 'D');
insert into section values ('CS-319', '1', 'Spring', '2018', 4, 'B');
insert into section values ('CS-319', '2', 'Spring', '2018', 3, 'C');
insert into section values ('CS-347', '1', 'Fall', '2017', 3, 'A');
insert into section values ('EE-181', '1', 'Spring', '2017', 3, 'C');
insert into section values ('FIN-201', '1', 'Spring', '2018', 1, 'B');
insert into section values ('HIS-351', '1', 'Spring', '2018', 2, 'C');
insert into section values ('MU-199', '1', 'Spring', '2018', 1, 'D');
insert into section values ('PHY-101', '1', 'Fall', '2017', 4, 'A');
insert into teaches values ('10101', 'CS-101', '1', 'Fall', '2017');
insert into teaches values ('10101', 'CS-315', '1', 'Spring', '2018');
insert into teaches values ('10101', 'CS-347', '1', 'Fall', '2017');
insert into teaches values ('12121', 'FIN-201', '1', 'Spring', '2018');
insert into teaches values ('15151', 'MU-199', '1', 'Spring', '2018');
insert into teaches values ('22222', 'PHY-101', '1', 'Fall', '2017');
insert into teaches values ('32343', 'HIS-351', '1', 'Spring', '2018');
insert into teaches values ('45565', 'CS-101', '1', 'Spring', '2018');
insert into teaches values ('45565', 'CS-319', '1', 'Spring', '2018');
insert into teaches values ('76766', 'BIO-101', '1', 'Summer', '2017');
insert into teaches values ('76766', 'BIO-301', '1', 'Summer', '2018');
insert into teaches values ('83821', 'CS-190', '1', 'Spring', '2017');
insert into teaches values ('83821', 'CS-190', '2', 'Spring', '2017');
insert into teaches values ('83821', 'CS-319', '2', 'Spring', '2018');
insert into teaches values ('98345', 'EE-181', '1', 'Spring', '2017');
insert into student values ('00128', 'Zhang', 'Comp. Sci.', '102');
insert into student values ('12345', 'Shankar', 'Comp. Sci.', '32');
insert into student values ('19991', 'Brandt', 'History', '80');
insert into student values ('23121', 'Chavez', 'Finance', '110');
insert into student values ('44553', 'Peltier', 'Physics', '56');
insert into student values ('45678', 'Levy', 'Physics', '46');
insert into student values ('54321', 'Williams', 'Comp. Sci.', '54');
insert into student values ('55739', 'Sanchez', 'Music', '38');
insert into student values ('70557', 'Snow', 'Physics', '0');
insert into student values ('76543', 'Brown', 'Comp. Sci.', '58');
insert into student values ('76653', 'Aoi', 'Elec. Eng.', '60');
insert into student values ('98765', 'Bourikas', 'Elec. Eng.', '98');
insert into student values ('98988', 'Tanaka', 'Biology', '120');
insert into takes values ('00128', 'CS-101', '1', 'Fall', '2017', 'A');
insert into takes values ('00128', 'CS-347', '1', 'Fall', '2017', 'A-');
insert into takes values ('12345', 'CS-101', '1', 'Fall', '2017', 'C');
insert into takes values ('12345', 'CS-190', '2', 'Spring', '2017', 'A');
insert into takes values ('12345', 'CS-315', '1', 'Spring', '2018', 'A');
insert into takes values ('12345', 'CS-347', '1', 'Fall', '2017', 'A');
insert into takes values ('19991', 'HIS-351', '1', 'Spring', '2018', 'B');
insert into takes values ('23121', 'FIN-201', '1', 'Spring', '2018', 'C+');
insert into takes values ('44553', 'PHY-101', '1', 'Fall', '2017', 'B-');
insert into takes values ('45678', 'CS-101', '1', 'Fall', '2017', 'F');
insert into takes values ('45678', 'CS-101', '1', 'Spring', '2018', 'B+');
insert into takes values ('45678', 'CS-319', '1', 'Spring', '2018', 'B');
insert into takes values ('54321', 'CS-101', '1', 'Fall', '2017', 'A-');
insert into takes values ('54321', 'CS-190', '2', 'Spring', '2017', 'B+');
insert into takes values ('55739', 'MU-199', '1', 'Spring', '2018', 'A-');
insert into takes values ('76543', 'CS-101', '1', 'Fall', '2017', 'A');
insert into takes values ('76543', 'CS-319', '2', 'Spring', '2018', 'A');
insert into takes values ('76653', 'EE-181', '1', 'Spring', '2017', 'C');
insert into takes values ('98765', 'CS-101', '1', 'Fall', '2017', 'C-');
insert into takes values ('98765', 'CS-315', '1', 'Spring', '2018', 'B');
insert into takes values ('98988', 'BIO-101', '1', 'Summer', '2017', 'A');
insert into takes values ('98988', 'BIO-301', '1', 'Summer', '2018', null);
insert into advisor values ('00128', '45565');
insert into advisor values ('12345', '10101');
insert into advisor values ('23121', '76543');
insert into advisor values ('44553', '22222');
insert into advisor values ('45678', '22222');
insert into advisor values ('76543', '45565');
insert into advisor values ('76653', '98345');
insert into advisor values ('98765', '98345');
insert into advisor values ('98988', '76766');
insert into time_slot values ('A', 'M', '08:00:00', '08:50:00');
insert into time_slot values ('A', 'W', '08:00:00', '08:50:00');
insert into time_slot values ('A', 'F', '08:00:00', '08:50:00');
insert into time_slot values ('B', 'M', '09:00:00', '09:50:00');
insert into time_slot values ('B', 'W', '09:00:00', '09:50:00');
insert into time_slot values ('B', 'F', '09:00:00', '09:50:00');
insert into time_slot values ('C', 'M', '11:00:00', '11:50:00');
insert into time_slot values ('C', 'W', '11:00:00', '11:50:00');
insert into time_slot values ('C', 'F', '11:00:00', '11:50:00');
insert into time_slot values ('D', 'M', '13:00:00', '13:50:00');
insert into time_slot values ('D', 'W', '13:00:00', '13:50:00');
insert into time_slot values ('D', 'F', '13:00:00', '13:50:00');
insert into time_slot values ('E', 'T', '10:30:00', '11:45:00');
insert into time_slot values ('E', 'R', '10:30:00', '11:45:00');
insert into time_slot values ('F', 'T', '14:30:00', '15:45:00');
insert into time_slot values ('F', 'R', '14:30:00', '15:45:00');
insert into time_slot values ('G', 'M', '16:00:00', '16:50:00');
insert into time_slot values ('G', 'W', '16:00:00', '16:50:00');
insert into time_slot values ('G', 'F', '16:00:00', '16:50:00');
insert into time_slot values ('H', 'W', '10:00:00', '12:30:00');
insert into prereq values ('BIO-301', 'BIO-101');
insert into prereq values ('BIO-399', 'BIO-101');
insert into prereq values ('CS-190', 'CS-101');
insert into prereq values ('CS-315', 'CS-101');
insert into prereq values ('CS-319', 'CS-101');
insert into prereq values ('CS-347', 'CS-101');
insert into prereq values ('EE-181', 'PHY-101');


-- Student CRUD /////////////////////////////////////////////////////////////////////

INSERT INTO student (stu_ID, name, dept_name, tot_cred)
VALUES(10011, "Goku", "Finance", 901);

SELECT * FROM student;

UPDATE student
SET tot_cred = 10
WHERE stu_id = 10011;

DELETE FROM student
WHERE stu_ID = 10011;

-- Takes CRUD //////////////////////////////////////////////////////////////////////

insert into takes (stu_ID, course_id, sec_id, semester, year, grade)
VALUES(10011, "FIN-201", 1, "Fall", 2017, "A+");

SELECT * FROM takes;

UPDATE takes
set grade = "A-"
WHERE stu_ID = 10011;

DELETE from takes
where stu_ID = 10011;

-- Instructor CRUD ///////////////////////////////////////////////////////////////////////

insert into instructor (ID, name, dept_name, salary)
VALUES(10011, "Goku", 1, "Finance", 100000);

SELECT * FROM instructor;

UPDATE instructor
set salary = 10000
WHERE ID = 10011;

DELETE from instructor
where ID = 10011;

-- department CRUD ////////////////////////////////////////////////////////

INSERT INTO department(dept_name, building, budget)
VALUES("Saiyans", "Painter", 100000.0);

select * FROM department;

UPDATE department
SET budget = 90000
WHERE dept_name = "Saiyans";

DELETE from department
WHERE dept_name = "Saiyans";

-- section CRUD ////////////////////////////////////////////////////////////

INSERT INTO section(course_id, sec_id, semester, year, roomID, time_slot_id)
VALUES("CS-101", 1, "Fall", 2018, 2, "A");

select * FROM section;

UPDATE section
SET time_slot_id = "B"
WHERE course_id = "CS-101" and semester = "Fall" and year = 2018 and sec_id = 2;

DELETE from section
WHERE course_id = "CS-101" and semester = "Fall" and year = 2018 and sec_id = 2;

-- Course CRUD ////////////////////////////////////////////////////

INSERT INTO course(course_id, title, dept_name, credits)
VALUES("SAI-101", "Intro to Saiyans", "Saiyans", 4);

select * FROM course;

UPDATE course
SET credits = 5
WHERE course_id = "SAI-101";

DELETE from course
WHERE course_id = "SAI-101";