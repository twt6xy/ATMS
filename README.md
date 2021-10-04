# ATMS
Portal into the Active Traffic Management System DB.

## Using the portal
* Step 1. import pandas, os, sys, and the AtmsPortal class
* Step 2. Initialize the database driver and connect to ATMS (must be on the Atlanta data centers VPN)
* Step 3. Wait for the "Successfully connected to ATMS" message.

![Alt text](https://github.com/twt6xy/ATMS/blob/main/atms1.PNG?raw=true)

### Pulling incidents view
* Step 4. Input the filters and wait for the "Query executed successfully!" message.

![Alt text](https://github.com/twt6xy/ATMS/blob/main/atms2.PNG?raw=true)

* Step 5. View the data

![Alt text](https://github.com/twt6xy/ATMS/blob/main/atms3.PNG?raw=true)

* Step 6. Data is in a Pandas dataframe so do whatever analysis you want.

![Alt text](https://github.com/twt6xy/ATMS/blob/main/atms4.PNG?raw=true)
