# UPGRADE_CPE_TOOL

Steps to run this Tool:

1) Install Supported packages
Pip install netmiko - for making connection to devices
Pip install pandas - for data manipulation

2) Folder structure:
UpgradeTool:
total 56
-rw-rw-r-- 1 sathish123 sathish123    0 Mar  2 16:10 __init__.py
-rw-rw-r-- 1 sathish123 sathish123  506 Mar  2 16:10 Variables.py
-rw-rw-r-- 1 sathish123 sathish123  148 Mar  2 16:10 templates.py
-rw-rw-r-- 1 sathish123 sathish123  297 Mar  2 16:27 templates.pyc
-rw-rw-r-- 1 sathish123 sathish123  655 Mar  2 16:27 Variables.pyc
-rw-rw-r-- 1 sathish123 sathish123 4343 Mar  6 16:23 Commands.py
-rw-rw-r-- 1 sathish123 sathish123 5330 Mar  6 16:48 Commands.pyc
drwxrwxr-x 2 sathish123 sathish123 4096 Mar  6 17:00 LOGS
-rw-rw-r-- 1 sathish123 sathish123 4953 Mar  6 17:00 UpgradeCpe.py
-rw-rw-r-- 1 sathish123 sathish123 5833 Mar  6 17:00 upgrade_device_list.xlsx
-rw-rw-r-- 1 sathish123 sathish123  196 Mar  6 17:05 README.md

3) Edit upgrade_device_list.xlsx
   add your CPEs & details and save.
4) Run UpgradeCpe.py

5) At the end of script run - SUMMARY REPORT will displayed & logged

6) Scripts Logs stored in ./LOGS folder