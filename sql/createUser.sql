CREATE USER 'makerhub'@'localhost' IDENTIFIED BY 'changeme';
GRANT ALL PRIVILEGES ON registerdb.* TO 'makerhub'@'localhost';
FLUSH PRIVILEGES;
