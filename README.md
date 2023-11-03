# Zwerfinator: Hasta la vista, plastic soup!

# Table of Contents
- [Introduction](#introduction)
- [1. Challenge Goal](#1-challenge-goal)
- [2. Insights based on exploratory analysis](#2-insights-based-on-exploratory-analysis)
- [3. Recommendations](#3-recommendations)
- [4. Project Details](#4-project-details)
  - [4.1 Defining the Plan](#41-defining-the-plan)
  - [4.2 Data preparation and cleaning](#42-data-preparation-and-cleaning)
  - [4.3 Dashboard development](#43-dashboard-development)
- [5. What I Have Learned](#5-what-i-have-learned)
- [6. Next Steps](#6-next-steps)
- [7. Images](#7-images)
- [8. Prerequisites for running the project](#8-prerequisites-for-running-the-project)
- [9. CBS Data License](#9-cbs-data-license)
- [10. Links](#10-links)

# Introduction

This repository contains the files for the Power BI project created for the "Dashboard Duel 1: Zwerfinator" challenge by Inergy and GetResponsive. The challenge is in collaboration with Zwerfinator, a well-known environmental activist in the Netherlands dedicated to making the country litter-free. Zwerfinator collects data about the litter he collects and uses this data to influence policies, educate children about his mission, and serve as a public speaker. The top 3 dashboards will actually be used, and therefore the challenge is also a direct contribution to his work and cause.

# 1. Challenge Goal

Zwerfinator's primary goal is to make the country litter-free through collecting and using data about litter. He releases periodic reports and runs targeted campaigns, such as demonstrating how the newly introduced national policy for deposits on soda cans influences producers to use alternative packaging that bypasses this obligation and is more harmful to the environment.

The challenge's primary objective is to

- Create an interactive dashboard that can be used in various research initiatives for governments and other institutions,
- A dashboard that can easily load other datasets.

**Deliverables:**

- An interactive dashboard to help Zwerfinator use his data more effectively in his mission to combat litter.
- A Power BI pbix file that supports the replacement of data in the dataset so that data from other cities can be easily incorporated.

# 2. Insights based on exploratory analysis

- The neighborhood "Dwarsgouw" had the most increase in total litter collected in 2022, closely followed by "Overwhere-Noord" and "Overwhere-Zuid."
- The biggest drivers of this increase were plastic and paper packaging, including plain pieces of paper, plastic wrappers, and plastic bags.
- The increase was most significant in the 3rd quarter of 2022.
- Looking at the same key drivers for all neighborhoods, the increase remains predominantly in "Dwarsgouw," followed by "Overwhere-Noord" and "Overwhere-Zuid."
- The increase seems to be specific to these neighborhoods; neighborhoods to the south even see a decrease.

# 3. Recommendations

It's essential to understand why there is an increase in litter in the form of plastic bags, wrappers, and pieces of paper, particularly in three key neighborhoods. This type of litter is easily thrown away in trash bins and could indicate a lack of sufficient trash bins or that they are not being emptied frequently enough. However, it could also mean that there are more sources of this type of litter in these areas.

I recommend collecting data on the number of trash bins and full trash bins found during follow-up collection runs to determine if the neighborhood may not facilitate enough litter collection or if other contributing factors, such as new shops opening or increased outdoor leisure activities, are leading to more litter being discarded.

# 4. Project Details

## 4.1 Defining the Plan

I started by learning more about Zwerfinator's work, how he uses his data, and cleaning and exploring the provided dataset. Based on the project goals, my initial plan was to build a multipage Power BI report that allows users to perform exploratory analysis and more detailed analysis. However, I found that the dataset's dimensions stood mostly on their own and had no significant relationships to one another, other than providing details about collected litter, including materials, types, and locations. Therefore, I decided to build an exploratory dashboard that delivers insights inspired by how he develops reports. This will ensure the business use case.

## 4.2 Data preparation and cleaning

Data preparation and cleaning involved importing datasets from an Excel workbook into separate tables, transforming and enhancing the data, and creating a data model. I made several changes to the data, such as removing empty rows, formatting text columns, and adding missing values to the dimension table "Merken" (brands). I also added a dynamic calendar table for filtering and normalization of the data model.

For the location data, I decided to use geographic coordinates to improve the quality and filtering options of the data. I obtained geographic information based on coordinates from the Central Bureau of Statistics (CBS) public API. However, integrating this data into the dataset presented some challenges.

To overcome these challenges, I used Python scripts in Power Query to handle the location data, including municipality, district, and neighborhood dimension tables, a mapping table for the dataset to the dimensions, and fact tables for surface area (m2). I stored these scripts in the Python folder in the repository.

# 4.3 Dashboard development

The dashboard was designed to provide exploratory analysis based on reports. It tells a story starting with cumulative KPI values for total litter and litter per kilometer, followed by the analysis of litter per location and a summary of core figures over the years. The dashboard then provides insights into key drivers and year-over-year changes per period (month or quarter) per selected location.

Two challenges encountered during dashboard development were the location data representation and incomplete weight data. To display the location data effectively, I used the filled map visual and created a custom TopoJSON map file. The weight data could not be mapped to other dimensions, but only to region and year because there was a difference in granularity for date information with the other data. On top of that, I also discovered that the data was missing a lot of data for locations, therefore this data stood too much on itself to provide meaningful insights through my dashboard, and I decided to completely remove the data from the data model.

# 5. What I Have Learned

In the course of this project, I acquired valuable skills and knowledge:

- I learned to use shape maps in Power BI, including the creation of TopoJSON files.
- I gained experience in successfully implementing API requests with Python in Power Query, including the use of parameters.
- I became proficient in working with geodata and the transformation of geospatial information using python library Geopandas. 

# 6. Next Steps

As next steps, I would recommend the following:

- Enhance the dashboard as desired. There are many more options available to obtain fact data from CBS that can enhance the analysis. Since the dashboard was built in a short period of time as part of a challenge, I suggest using the dashboard and making adjustments when needed.
- The dataset contains weight data that could not be connected to the other data. I would enhance the dimension tables with a column for weight (how much does each piece of litter weigh). This would allow the calculation of total weight, even though there could be some inaccuracies, I don't think this would be significant.
- The dimension tables in the dataset contained duplicate values due to inconsistent use of cases, spaces, and symbols. I suggest cleaning up the tables in the Excel workbook and keeping them regularly updated. This will enhance accuracy.

# 7. Images

Here are some pictures from the project:

- Analysis Bookmark 1
  ![Analysis Bookmark 1](https://github.com/NdeWinter/dashboard-duel-zwerfinator/raw/main/Screenshots/Analysis%20Bookmark%201.png)

- Analysis Bookmark 2
  ![Analysis Bookmark 2](https://github.com/NdeWinter/dashboard-duel-zwerfinator/raw/main/Screenshots/Analysis%20Bookmark%202.png)

- Analysis Bookmark 3
  ![Analysis Bookmark 3](https://github.com/NdeWinter/dashboard-duel-zwerfinator/raw/main/Screenshots/Analysis%20Bookmark%203.png)

- Analysis Bookmark 4
  ![Analysis Bookmark 4](https://github.com/NdeWinter/dashboard-duel-zwerfinator/raw/main/Screenshots/Analysis%20Bookmark%204.png)

# 8. Prerequisites for running the project

To use the project files, the following needs to be installed on your desktop:

- **Power BI Desktop:** You will need Power BI Desktop to interact with and customize the interactive dashboard.
- **Python:** Some data preprocessing is done by Python in Power Query.
- **Excel:** Excel may be used for exploring the dataset.

For Python, the following libraries need to be installed:

- Requests
- Pandas
- Geopandas
- Shapely

In addition, I have included the Python scripts I used in Power Query and seperate scripts that can be used standalo, including a class script, for requesting location data from The Netherlands and integrating the data with your existing workbook.

# 9. CBS Data License

In this project, geographic data from the Central Bureau of Statistics (CBS) was used. It's important to note that CBS data is open for use through the PDOK webservice.

# 10. Links

- [The Dashboard Challenge Page](https://inergy.nl/dashboard-duel/#msdynttrid=sewInFgnAQHPu4TD-2UENceaUYWM-Ahsa7HdciuH3yw)
- [Zwerfinator Website](https://www.zwerfinator.nl)
- [Converting CSV to TopoJSON](https://geojson.io)
- [PDOK webservice for CBS Data](https://www.pdok.nl/ogc-webservices/-/article/cbs-gebiedsindelingen#1dd45ad87a8113e6e3ddf0723696c627)
