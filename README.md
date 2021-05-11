#10KTxtFileLinks.csv
This contains the results from SEC_Scrap_TxtFiles.py.
As of right now it contains the 10K txt files for 100 different companies that have reported 10Ks.
Something important to note is that some txt files need to be processed through BeautifulSoup, while older documents come already in a readable format. 

#SEC_Scraper.py
One important thing to note is that the SEC will sometimes block requests to pull data if you don't define your user agent. 
Works fine, but some of the parsing needs some additional working on. 
Furthermore, the csv file related to this (10KParseData) does not look the greatest. 
I recommend looking at the Dataframe for the master_data element to get a better idea of what I want the finished product to look like. 

#10KParseData.csv
Please refer to the Dataframe for the master_data element in SEC_Scraper.py
