CREATE TABLE Students (
    StudentID INT PRIMARY KEY,
    Name VARCHAR(100),
    Department VARCHAR(50),
    Email VARCHAR(100) UNIQUE
);

CREATE TABLE Faculty (
    FacultyID INT PRIMARY KEY,
    Name VARCHAR(100),
    Department VARCHAR(50)
);

CREATE TABLE Courses (
    CourseID INT PRIMARY KEY,
    Title VARCHAR(100),
    Credits INT,
    FacultyID INT,
    FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID)
);

CREATE TABLE Enrollments (
    EnrollmentID INT PRIMARY KEY,
    StudentID INT,
    CourseID INT,
    Semester VARCHAR(10),
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

CREATE TABLE Attendance (
    AttendanceID INT PRIMARY KEY,
    StudentID INT,
    CourseID INT,
    ClassesHeld INT,
    ClassesAttended INT,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

CREATE TABLE Marks (
    MarksID INT PRIMARY KEY,
    StudentID INT,
    CourseID INT,
    InternalMarks INT,
    ExternalMarks INT,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);

INSERT INTO Students VALUES
(1, 'Aarav', 'CSE', 'aarav@example.com'),
(2, 'Diya', 'ECE', 'diya@example.com'),
(3, 'Rohit', 'MECH', 'rohit@example.com');

INSERT INTO Faculty VALUES
(101, 'Dr. Sharma', 'CSE'),
(102, 'Prof. Mehta', 'ECE');

INSERT INTO Courses VALUES
(1001, 'Database Systems', 4, 101),
(1002, 'Data Structures', 3, 101),
(1003, 'Digital Electronics', 4, 102);

INSERT INTO Enrollments VALUES
(1, 1, 1001, '5'),
(2, 1, 1002, '5'),
(3, 2, 1003, '3');

INSERT INTO Attendance VALUES
(1, 1, 1001, 40, 36),
(2, 1, 1002, 42, 39),
(3, 2, 1003, 38, 34);

INSERT INTO Marks VALUES
(1, 1, 1001, 40, 48),
(2, 1, 1002, 35, 42),
(3, 2, 1003, 38, 50);

CREATE VIEW StudentCourseView AS
SELECT s.Name, c.Title, e.Semester
FROM Students s
JOIN Enrollments e ON s.StudentID = e.StudentID
JOIN Courses c ON e.CourseID = c.CourseID;

CREATE VIEW PerformanceSummary AS
SELECT s.StudentID, s.Name,
       AVG(m.InternalMarks + m.ExternalMarks) AS AvgScore
FROM Students s
JOIN Marks m ON s.StudentID = m.StudentID
GROUP BY s.StudentID;

DELIMITER $$

CREATE FUNCTION GetGrade(total INT)
RETURNS CHAR(1)
DETERMINISTIC
BEGIN
    DECLARE grade CHAR(1);

    IF total >= 90 THEN SET grade = 'A';
    ELSEIF total >= 75 THEN SET grade = 'B';
    ELSEIF total >= 60 THEN SET grade = 'C';
    ELSE SET grade = 'D';
    END IF;

    RETURN grade;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER ValidateMarks
BEFORE INSERT ON Marks
FOR EACH ROW
BEGIN
    IF NEW.InternalMarks < 0 OR NEW.InternalMarks > 50 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid Internal Marks';
    END IF;

    IF NEW.ExternalMarks < 0 OR NEW.ExternalMarks > 50 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid External Marks';
    END IF;
END $$

DELIMITER ;

-- 1. Students with enrolled courses
SELECT s.Name, c.Title FROM Students s
JOIN Enrollments e ON s.StudentID = e.StudentID
JOIN Courses c ON e.CourseID = c.CourseID;

-- 2. Attendance percentage
SELECT StudentID, CourseID, 
       (ClassesAttended / ClassesHeld) * 100 AS AttendancePercent
FROM Attendance;

-- 3. Generate grade using SQL function
SELECT StudentID, CourseID,
       GetGrade(InternalMarks + ExternalMarks) AS Grade
FROM Marks;

-- 4. Students scoring above 80%
SELECT s.Name FROM Students s
JOIN Marks m ON s.StudentID = m.StudentID
WHERE (m.InternalMarks + m.ExternalMarks) > 80;

-- 5. Average marks per course
SELECT CourseID, AVG(InternalMarks + ExternalMarks) AS AvgScore
FROM Marks GROUP BY CourseID;

-- 6. Low attendance students
SELECT StudentID FROM Attendance
WHERE (ClassesAttended / ClassesHeld) * 100 < 75;

-- 7. Faculty teaching multiple courses
SELECT FacultyID, COUNT(*) FROM Courses GROUP BY FacultyID HAVING COUNT(*) > 1;

-- 8. Students not enrolled in any course
SELECT * FROM Students WHERE StudentID NOT IN (SELECT StudentID FROM Enrollments);

-- 9. Total students per department
SELECT Department, COUNT(*) FROM Students GROUP BY Department;

-- 10. Courses with highest credits
SELECT Title FROM Courses ORDER BY Credits DESC LIMIT 1;

-- 11. Student-wise average marks
SELECT s.Name, AVG(m.InternalMarks + m.ExternalMarks)
FROM Students s JOIN Marks m ON s.StudentID = m.StudentID
GROUP BY s.Name;

-- 12. Course enrollment count
SELECT CourseID, COUNT(*) FROM Enrollments GROUP BY CourseID;

-- 13. Students taking more than 1 course
SELECT StudentID, COUNT(*) FROM Enrollments GROUP BY StudentID HAVING COUNT(*) > 1;

-- 14. Best performing student
SELECT Name FROM Students
WHERE StudentID = (SELECT StudentID FROM PerformanceSummary ORDER BY AvgScore DESC LIMIT 1);

-- 15. Student details with faculty
SELECT s.Name, c.Title, f.Name AS Faculty
FROM Students s
JOIN Enrollments e ON s.StudentID = e.StudentID
JOIN Courses c ON c.CourseID = e.CourseID
JOIN Faculty f ON f.FacultyID = c.FacultyID;

-- 16. Courses with no enrollments
SELECT * FROM Courses WHERE CourseID NOT IN (SELECT CourseID FROM Enrollments);

-- 17. Students with grade 'A'
SELECT StudentID, GetGrade(InternalMarks + ExternalMarks) 
FROM Marks HAVING GetGrade(InternalMarks + ExternalMarks) = 'A';

-- 18. Update attendance automatically (example update)
UPDATE Attendance SET ClassesAttended = ClassesAttended + 1 WHERE StudentID = 1;

-- 19. Delete enrollments for a withdrawn student
DELETE FROM Enrollments WHERE StudentID = 3;

-- 20. Increase credits for advanced courses
UPDATE Courses SET Credits = Credits + 1 WHERE Credits < 4;

