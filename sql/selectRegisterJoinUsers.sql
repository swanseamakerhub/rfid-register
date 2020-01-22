SELECT register.DateTime, users.FirstName, users.LastName, users.StudentNo, users.LevelID, users.CourseID FROM register INNER JOIN users on register.UserID=users.UserID;


