# Project Name: Web-Scraping-ScienceWebSites-Analysis

## Table of Contents
- [Overview](#Overview)
- [Requirements](#Requirements)
- [ScienceDirect Scraper](#ScienceDirect-Scraper)
- [Nature Scraper](#Nature-Scraper)
- [Execution Time](#Execution-Time)
- [Note](#Note)

## Overview
This repository contains Python scripts for web scraping scientific articles related to specific topics from two different websites: ScienceDirect and Nature. The purpose is to analyze and collect information such as article titles, authors, publication dates, and contents for further research and analysis.

## Requirements
Make sure you have the required Python libraries installed before running the scripts. You can install them using the following command:

    pip install scrapy undetected-chromedriver selenium seleniumwire

## ScienceDirect Scraper
### Script: sciencedirect_disease-name.py
### Description
This script scrapes articles related to manu diseases from ScienceDirect. It performs a search query for disease-name and extracts relevant information from the search results.

### Usage
Run the script using the following command:

    python sciencedirect_disease-name.py
### Data Output
Scraped data is saved in JSON format in the file sciencedirect_disease-name.json.
Additional details such as authors and article content are appended to the existing JSON file.



## Nature Scraper
### Script: nature_disease-name.py
### Description
This script scrapes articles related to manu diseases from Nature. It performs a search query for disease-name and extracts relevant information from the search results.

### Usage
Run the script using the following command:

    python nature_disease-name.py

### Data Output
Scraped data is saved in JSON format in the file nature_disease-name.json.
Additional details such as authors and article content are appended to the existing JSON file.


## Execution Time
The scripts provide information about the execution time at the end of the output.

## Note
Please be aware of the legal and ethical implications of web scraping. Make sure to review the terms of service of the websites being scraped and ensure compliance with their policies.
