#!/bin/bash

(mysql -u makerhub -p registerdb < selectRegisterJoinUsers.sql) > export.txt
