#!/usr/bin/env python
# coding: utf-8

# In[3]:


import cx_Oracle
import pandas as pd
from IncidentPortal import IncidentPortal

'''
Driver class for accessing the ATMS database via Python.
This assumes you are already connected to the ATL data center VPN.
'''
class AtmsPortal:
    
    # initialize the portal with ATMS login and routing info
    def __init__(self, conn=None, cur=None):
        self.conn = conn
        self.cur = cur
    
    # connect to the ATMS database
    def connect(self):
        
        # read in the credentials
        with open('../.credentials') as f:
            credentials = f.read()
            lines = credentials.split("\n")
            username = lines[0]
            password = lines[1]
            uri = lines[2]
            port = lines[3]
            db_name = lines[4]
        
        result = None
        while result == None:
            try:
                self.conn = cx_Oracle.connect(f'{username}/{password}@//{uri}:{port}/{db_name}')
                print("Successfully connected to ATMS.")
                result = 1
                
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                if error.code == 12170:
                    #print("Timeout Error: This is common with ATMS, try again until it connects.")
                    print("Timeout Error: trying again...")
                else:
                    print("Database connection error: %s".format(e))
                pass
        try:        
            self.cur = self.conn.cursor()
        except AttributeError:
                print("")
    
    # disconnect from the ATMS database
    def disconnect(self):
        self.cur.close()
        self.conn.close()
    
    # provide a query and save the output into a pandas dataframe
    def getQuery(self, query):
        df = pd.read_sql(query, con=self.conn)
        return df
    
    # get a clean incidents table with geographic location and lane information
    def getCleanedIncidentTable(self):
        incidents = IncidentPortal(self)
        return incidents

