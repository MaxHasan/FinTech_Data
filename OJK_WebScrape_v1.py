#!/usr/bin/env python
# coding: utf-8

# In[89]:


#####Step 1: start by importing all of the necessary packages#####
import requests #requesting URLs
import urllib.request #requesting URLs
import time #setting the speed at which the requests run
import re #regexp string manipulation
import pandas as pd #for simplifying data operations (e.g. creating dataframe objects)
import matplotlib.pyplot as plt #for plotting the scraped data
from bs4 import BeautifulSoup #for web-scraping operations


# In[2]:


#####Step 2: connect to the URL that you are interested in scraping#####
url = 'https://www.ojk.go.id/id/kanal/iknb/data-dan-statistik/fintech/Default.aspx' 
response = requests.get(url) #Connect to the URL using the "requests" package
response #if successful then it will return 200


# In[3]:


#####Step 3: read in the URL via the "BeautifulSoup" package#####
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)


# In[4]:


#####Step 4: filter the "BeautifulSoup" HTML object for all link objects#####
link_objs = soup.find_all('a',href=re.compile('/id/kanal/iknb/data-dan-statistik/fintech/Pages'))


# In[5]:


#####Step 5: loop through the link objects of interest with regexp operations to download#####
#Step 5a: iterate through the index of the list
for i in range(len(link_objs)):
    #Step 5b: pass each respective item through a string object
    str_link = str(link_objs[i])
    #Step 5c: create a start index for the string
    start_index = re.search(r"\bPages/",str_link)
    #Step 5d: create an end index for the string
    end_index = re.search(r"\"",str_link[start_index.span()[0]:len(str_link)])
    #Step 5e: set the initial url using the start and end indices above
    end_url = str_link[start_index.span()[0]+6:start_index.span()[0]+end_index.span()[0]]
    #Step 5f: because the Excel files are actually nested in a additional links, we need to iterate through sub-urls
    sub_url = 'https://www.ojk.go.id/id/kanal/iknb/data-dan-statistik/fintech/Pages/'+end_url
    #Step 5g: pass the sub-url webpage through the "BeautifulSoup" html parser
    sub_soup = BeautifulSoup(requests.get(sub_url).text, 'html.parser')
    #Step 5h: search through the html object to find all Excel files in question
    sub_soup_link = sub_soup.find('a',href=re.compile('xlsx'))
    #Step 5i: convert the files into string objects for passing through the URL retrieve function
    str_sub_soup_link = re.search(r'=\"(.*?)xlsx', str(sub_soup_link)).group(1)
    #Step 5j: create a download URL object
    download_url = 'https://www.ojk.go.id'+str_sub_soup_link+'xlsx'
    #Step 5k: declare a file name
    file_name = str_sub_soup_link[re.search(r'Documents',str_sub_soup_link).span()[1]+1:len(str_sub_soup_link)]+'xlsx'
    #Step 5l: request and retrieve the respective Excel file into a given file & folder location (this can be modified as needed)
    urllib.request.urlretrieve(download_url,'/Users/maxha/Downloads/'+file_name) #make sure that you modify this script such that it reflects the filepath of your choice
    #Step 5m: using the "time" package
    time.sleep(1)


# In[6]:


###############################################################################
#####BONUS! create a dual y-axis chart to visualize the latest file's KPIs#####
###############################################################################
#####Step 6: load the latest file into a dataframe#####
#Step 6a: locate the latest file; given ordering, it's the 10th to last, not the last
last_file = len(link_objs)-10
#Step 6b: convert the last file address into a string
str_link = str(link_objs[last_file])
#Step 6c: create a start index for the string
start_index = re.search(r"\bPages/",str_link)
#Step 6d: create an end index for the string
end_index = re.search(r"\"",str_link[start_index.span()[0]:len(str_link)])
#Step 6e: set the initial url using the start and end indices above
end_url = str_link[start_index.span()[0]+6:start_index.span()[0]+end_index.span()[0]]
#Step 6f: because the Excel files are actually nested in a additional links, we need to iterate through sub-urls
sub_url = 'https://www.ojk.go.id/id/kanal/iknb/data-dan-statistik/fintech/Pages/'+end_url
#Step 6g: pass the sub-url webpage through the "BeautifulSoup" html parser
sub_soup = BeautifulSoup(requests.get(sub_url).text, 'html.parser')
#Step 6h: search through the html object to find all Excel files in question
sub_soup_link = sub_soup.find('a',href=re.compile('xlsx'))
#Step 6i: convert the files into string objects for passing through the URL retrieve function
str_sub_soup_link = re.search(r'=\"(.*?)xlsx', str(sub_soup_link)).group(1)
#Step 6j: create a download URL object
download_url = 'https://www.ojk.go.id'+str_sub_soup_link+'xlsx'
#Step 6k: create a dataframe object with the Excel file using the "Pandas" package
latest_file = pd.read_excel(download_url,
                            skiprows=3,
                            index_col=1
                           )


# In[113]:


#####Step 7: visualize the data with a dual-axis#####
#Step 7a: create the plot area dimensions
fig, ax = plt.subplots(figsize=(11,5))
#Step 7b: set the x-axis labels
ax.set_xticklabels('Month & Year',rotation=0, fontsize=10)
ax.set_xlabel('Month & Year')
#Step 7c: create a Series object from the TWP 90 (PAR 90) row of data
twp_90 = latest_file.loc['TWP 90','Desember 2019':'Desember 2020']
#Step 7d: convert the PAR 90 data into a percentage
twp_90 = twp_90*100
#Step 7e: create a Series object from the outstanding row of data
outstanding = latest_file.iloc[14,1:14]
#Step 7f: divide the outstanding amount by 1 trillion to simplify the display
outstanding = outstanding/1000000000000
#Step 7g: plot the outstanding with a gray barchart against the left y-axis
ax = outstanding.plot(kind='bar',color='gray')
#Step 7h: set the outstanding label
ax.set_ylabel('Rupiah outstanding (in trillions)',color='gray')
#Step 7i: set the dual y-axis plot up
ax2 = ax.twinx()
#Step 7j: plot the PAR 90 with a red line chart against the right y-axis
ax2 = twp_90.plot(kind="line",color="red")
#Step 7k: set the PAR 90 label
ax2.set_ylabel('PAR 90 in %',color="red")
#Step 7l: create the title label
plt.title("OJK FinTech Lending Industry KPIs")
#Step 7m: display the combined chart
plt.show()

