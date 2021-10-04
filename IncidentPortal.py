# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 18:11:21 2021

HELPER METHODS TO PULL THE MASTER ATMS INCIDENT TABLE WITHOUT OVERCROWDING THE ATMS PORTAL CLASS


@author: Will.Tyree
"""
import pandas as pd
import numpy as np
import sys
import plotly.express as px

def getUserInputForIncidents(self):
    q1 = "SELECT * FROM OPENTMS_USER.V_RPT_INCIDENT_DETAILS \
    INNER JOIN OPENTMS_USER.V_INCIDENT_LOCATION \
    ON OPENTMS_USER.V_RPT_INCIDENT_DETAILS.INCIDENT_ID = OPENTMS_USER.V_INCIDENT_LOCATION.INCIDENT_ID \
    INNER JOIN OPENTMS_USER.V_RDOM_INCIDENT_LANES \
    ON OPENTMS_USER.V_RPT_INCIDENT_DETAILS.INCIDENT_ID = OPENTMS_USER.V_RDOM_INCIDENT_LANES.INCIDENT_ID "
        
    filter_bool = input("Would you like to filter for a certain date range? (Y/N)\n")
    if filter_bool == 'Y':
        filter_criteria = input("\nSelect the number of the type of filter you would like to apply:\n 1. Specific year\n 2. Specific month within a year\n 3. Multiple years\n 4. Multiple months within a year\n 5. I want to compare the same month throughout different years.\n")
        if filter_criteria == '1':
            year = input("What year would you like to pull incidents for?\n")
            query = q1 + "WHERE event_year = " + year
        elif filter_criteria == '2':
            month = input("\nWhat month would you like to pull incidents for? (Ex. 1 for January, 2 for February, etc.)\n")
            year = input("\nWhich year would you like to pull incidents for "+month+"?\n")
            query = q1 + "WHERE (event_year = " + year + ") AND (event_month = " + month + ")"
        elif filter_criteria == '3':
            years = []
            n = int(input("\nEnter number of years: "))
            for i in range(0, n):
                year = input("Enter year " + str(i+1) + ": ")
                years.append(year)
            query = q1 + "WHERE event_year IN " + str(tuple(years))
        elif filter_criteria == '4':
            months = []
            n = int(input("\nEnter number of months: "))
            for i in range(0, n):
                month = input("Enter numerical month value " + str(i+1) + ": ")
                months.append(month)
            year = input("What year would you like to pull these months incidents for?\n")
            query = q1 + "WHERE (event_year = " + year + ") AND (event_month IN " + str(tuple(months)) + ")"
        elif filter_criteria == '5':
            years = []
            n = int(input("\nEnter number of years: "))
            for i in range(0, n):
                year = input("Enter year " + str(i+1) + ": ")
                years.append(year)
            month = input("What month would you like to pull these years incidents for?\n")
            query = q1 + "WHERE (event_month = " + month + ") AND (event_year IN " + str(tuple(years)) + ")"
        else:
            print("\nInvalid entry. Please input a number 1-5 with no spaces.")
            sys.exit()
    elif filter_bool == 'N':
        double_check = input("\nAre you sure you want to pull all available incident data in ATMS? (Y/N)\n")
        if double_check == 'Y':
            query = q1
        elif double_check == 'N':
            print("\nProgram shutting down. run it again, typing in 'Y' at the first prompt this time.")
            sys.exit()
        else:
            print("\nInvalid input. Shutting program down. Try again using only 'Y' or 'N' with no spaces.")
            sys.exit()
    else:
        print("\nInvalid input. Shutting program down. Try again using only 'Y' or 'N' with no spaces.")
        sys.exit()
        
    agency_bool = input("\nWould you like to pull the agency and responder data associated with this table? (Y/N)\n")
    print("\nExecuting the following query:\n"+query)
    
    if agency_bool == 'Y':
        print("\nPulling associated responder data...")
        agency_query = "SELECT * FROM OPENTMS_USER.V_RPT_INCIDENT_AGENCY"
        agency = self.getQuery(agency_query)
    elif agency_bool == 'N':
        agency = None
    else:
        ("\nInvalid input. Shutting program down. Try again using only 'Y' or 'N' with no spaces.")
        sys.exit()
    
    inc_details = self.getQuery(query)
    inc_details = inc_details.loc[:,~inc_details.columns.duplicated()]
    
    if agency is not None:
        agency_bool = agency.INCIDENT_ID.isin(inc_details.INCIDENT_ID)
        agency = agency[agency_bool]
        
    return inc_details, agency

def transformPointObjectToLatLongColumns(df):
    print("\nTransforming location point object into latitude and longitude columns...")
    df['LOCATION_ROADWAY_POINT_POINT'] = df['LOCATION_ROADWAY_POINT_POINT'].map(lambda x: x.lstrip('POINT(').rstrip(')'))
    df['LOCATION_ROADWAY_POINT_POINT'] = df['LOCATION_ROADWAY_POINT_POINT'].str.replace(r'(', '', regex=True)
    df[['LONGITUDE','LATITUDE']] = df['LOCATION_ROADWAY_POINT_POINT'].str.split(expand=True)
    df['LATITUDE'] = pd.to_numeric(df['LATITUDE'])
    df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'])
    df.drop('LOCATION_ROADWAY_POINT_POINT', axis=1, inplace=True)
    return df

def createLaneImpactingBoolean(df):
    print("\nCreating a boolean lane impacting (Y/N) column for easy filtering...")
    df["LANE_IMPACTING_BOOL"] = np.where(
        (df.TRAVEL_LANES_CLOSED > 0), 
        "Y", 
        "N"
    )
    return df

def condenseLaneInformation(df):
    print("\nCondensing the lane data into fewer columns...")
    df['TOTAL_TRAVEL_LANES'] = df.apply(applyTotalLanes, axis=1)
    df['TOTAL_TRAVEL_LANES_OPPOSITE'] = df.apply(applyTotalOppositeLanes, axis=1)
    df['TRAVEL_LANES_CLOSED'] = df.apply(applyTravelLanesClosed, axis=1)
    df['TRAVEL_LANES_CLOSED_OPPOSITE'] = df.apply(applyTravelLanesClosedOpposite, axis=1)
    df['SHOULDERS_CLOSED'] = df.apply(applyShouldersClosed, axis=1)
    df['SHOULDERS_CLOSED_OPPOSITE'] = df.apply(applyShouldersClosedOpposite, axis=1)
    df['CLOSED_RAMPS'] = df['CLOSED_ON_RAMPS'] + df['CLOSED_OFF_RAMPS']
    return df

def dropColumns(df):
    print("\nDropping unnecessary columns...")
    cols_to_keep = [
        'INCIDENT_ID', 'REGION', 'DISTRICT','JURISDICTION', 'LATITUDE', 'LONGITUDE', 'ROUTE_TYPE', 'DIRECTION',
        'EVENT_TYPE', 'ROUTE_NAME', 'MILE_MARKER', 'DETECTION_SOURCE', 'SEVERITY', 'PRIORITY', 'FATALITIES',
        'INJURIES', 'VEHICLE_COUNT', 'POC_NAME', 'LAST_UPDATED', 'ACTUAL_CLEAR_TIME', 'SCENE_CLEAR_TIME',
        'STR_TIME_CREATED', 'STR_TIME_VERIFIED', 'STR_TIME_STARTED', 'STR_TIME_ENDED', 'STR_TIME_FINAL', 'LC_DURATION', 'SC_DURATION',
        'HAZMAT_SIGNIFICANCE', 'CARGO_SPILL', 'HAZMAT_TYPE', 'CONFIRMED_BY', 'NARRATIVE_ID', 'EXT_ROUTE_NAME',
        'TOTAL_TRAVEL_LANES', 'TOTAL_TRAVEL_LANES_OPPOSITE', 'TRAVEL_LANES_CLOSED', 'TRAVEL_LANES_CLOSED_OPPOSITE',
        'SHOULDERS_CLOSED', 'SHOULDERS_CLOSED_OPPOSITE','CLOSED_ON_RAMPS', 'CLOSED_OFF_RAMPS', 'CLOSED_RAMPS',
        'CLOSED_TRAVEL_LANES', 'CLOSED_SHLDR_LANES', "LANE_IMPACTING_BOOL"
    ]
    df = df[cols_to_keep]
    
    rename_cols = {
        'STR_TIME_VERIFIED':'TIME_VERIFIED',
        'STR_TIME_CREATED':'TIME_CREATED',
        'STR_TIME_STARTED':'TIME_STARTED',
        'STR_TIME_ENDED':'TIME_ENDED',
        'STR_TIME_FINAL':'TIME_FINAL'}
    
    df = df.rename(columns=rename_cols)
    return df

def promptUserToSaveDataframe(df, df2=None):
    print("\nQuery executed successfully!\n")
    print(f"There are {len(df)} incidents within the data you requested, and {len(df.columns)} columns explaining the conditions of the incidents.\n")
    
    save_bool = input("Would you like to save this data now? (Y/N)\n")
    if save_bool == 'Y':
        title = input("\nWhat would you like the incidents data title to be? (No spaces and end with .csv, ex. incidents.csv)\n")
        df.to_csv("./"+title)
        print("\nYour incident csv file has been saved to this directory!")
        if df2 is not None:
            title = input("\nWhat would you like the responder data title to be? (No spaces and end with .csv, ex. incidents.csv)\n")
            df.to_csv("./"+title)
            print("\nYour responder csv file has been saved to this directory!")
    else:
        print("\nOk, the requested dataframe instances are within this notebook.")

def IncidentPortal(self):
    incidents, agency = getUserInputForIncidents(self)
    incidents = transformPointObjectToLatLongColumns(incidents)
    incidents = condenseLaneInformation(incidents)
    incidents = createLaneImpactingBoolean(incidents)
    incidents = dropColumns(incidents)
    promptUserToSaveDataframe(incidents, agency)
    return incidents, agency
    
# helper to condense the number of lane columns in the incidents data
def applyTotalLanes(row):
    if row['DIRECTION'] == 'NORTH':
        return row['NB_TOT_TRAVEL_LANES']
    elif row['DIRECTION'] == 'SOUTH':
        return row['SB_TOT_TRAVEL_LANES']
    elif row['DIRECTION'] == 'EAST':
        return row['EB_TOT_TRAVEL_LANES']
    else:
        return row['WB_TOT_TRAVEL_LANES']

# helper to condense the number of lane columns in the incidents data
def applyTotalOppositeLanes(row):
    if row['DIRECTION'] == 'NORTH':
        return row['SB_TOT_TRAVEL_LANES']
    elif row['DIRECTION'] == 'SOUTH':
        return row['NB_TOT_TRAVEL_LANES']
    elif row['DIRECTION'] == 'EAST':
        return row['WB_TOT_TRAVEL_LANES']
    else:
        return row['EB_TOT_TRAVEL_LANES']
    
def applyTravelLanesClosed(row):
    if row['DIRECTION'] == 'NORTH':
        return row['NB_CLOSED_TRAVEL_LANES']
    elif row['DIRECTION'] == 'SOUTH':
        return row['SB_CLOSED_TRAVEL_LANES']
    elif row['DIRECTION'] == 'EAST':
        return row['EB_CLOSED_TRAVEL_LANES']
    else:
        return row['WB_CLOSED_TRAVEL_LANES']
    
def applyTravelLanesClosedOpposite(row):
    if row['DIRECTION'] == 'NORTH':
        return row['SB_CLOSED_TRAVEL_LANES']
    elif row['DIRECTION'] == 'SOUTH':
        return row['NB_CLOSED_TRAVEL_LANES']
    elif row['DIRECTION'] == 'EAST':
        return row['WB_CLOSED_TRAVEL_LANES']
    else:
        return row['EB_CLOSED_TRAVEL_LANES']
    
def applyShouldersClosed(row):
    if row['DIRECTION'] == 'NORTH':
        return row['NB_CLOSED_SHLDR_LANES']
    elif row['DIRECTION'] == 'SOUTH':
        return row['SB_CLOSED_SHLDR_LANES']
    elif row['DIRECTION'] == 'EAST':
        return row['EB_CLOSED_SHLDR_LANES']
    else:
        return row['WB_CLOSED_SHLDR_LANES']
    
def applyShouldersClosedOpposite(row):
    if row['DIRECTION'] == 'NORTH':
        return row['SB_CLOSED_SHLDR_LANES']
    elif row['DIRECTION'] == 'SOUTH':
        return row['NB_CLOSED_SHLDR_LANES']
    elif row['DIRECTION'] == 'EAST':
        return row['WB_CLOSED_SHLDR_LANES']
    else:
        return row['EB_CLOSED_SHLDR_LANES']