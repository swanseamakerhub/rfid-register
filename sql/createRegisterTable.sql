CREATE TABLE register
(RegisterID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
DateTime datetime NOT NULL,
UserID int NOT NULL,
FOREIGN KEY (UserID) REFERENCES users(UserID);
