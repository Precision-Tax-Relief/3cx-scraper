# Serverless 3CX Scraper

This is a tool that uses Selenium and AWS Lambda that scrapes a booker account for customer appointments and orders.
It then sends this data to Segment using my fork of their python API library.

The bin directory contains scripts for testing and deploying the lambda function.\
lamdba_function.py is the entry point for the lambda function.\
scrapers.py contains the code for scraping the booker account.\
parser.py contains the code for parsing the scraped CSV exports.