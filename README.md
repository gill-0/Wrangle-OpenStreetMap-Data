# Wrangle-OpenStreetMap-Data

## Introduction

The goal of this project was to extract data from https://www.openstreetmap.org (open source database similar  to Google Maps) for an area of the world I am interested in. I then assessed the quality of the data for validity, accuracy, completeness, consistency and uniformity. Finally I imported the data into a SQL database for further querying and auditing. 

## Data Extraction, Cleaning, and Database Queries
Below is a blocks link that demonstrates the data extraction and cleaning process as well as database queries. 

http://bl.ocks.org/gill-0/raw/9c92a05cc3492a6e4985e3ce2565e801/

## Files

Audit different fields in OSM/XML file
```{r}
audit.py
```
Modify incorrect fields in OSM file and export to CSV files
```{r}
data.py
```
Import CSV files into database
```{r}
import_csv.py
```
Query and edit incorrect fields in database 
```{r}
query_functions.py
```
Database schema provided by Udacity
```{r}
schema.py
```
SQL queries to explore database
```{r}
sql_query.py
```

Discover structure and number of tags in OSM file
```{r}
map_parser.py
```

High level audit of tags for types of potential problems

```{r}
tags.py
```
Function to discover number of users

```{r}
users.py
```
Smaller OSM/XML file used for testing
```{r}
sample.osm
```
