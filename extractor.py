#Purpose: Find contact information for Marketting purposes
#This script is capable of extracting every single Psychotherapist in Canada
#With the help of selenium-chromeWebDriver and beautifulSoup
#Extracts all the public records and makes a Json file and CSV file


#TODO make a database out of CSV file.
#TODO Its not heavy on the computer but can increase speed of the script
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
import math
import re
from cities import get_cities 
cities = get_cities()
#url specific edit: '%20' for all the spaces 
cities = [city.replace(' ', '%20') for city in cities]

chrome_options = Options()
chrome_options.add_argument("--headless")


driver = webdriver.Chrome(options=chrome_options)

#Get Total number of pages from one city. 
for city in cities:
   gettingNumOfpages = f"https://registration.crpo.ca/mpower/mpp/member-directory-search.action?s={city}"
   driver.get(gettingNumOfpages)
   driver.implicitly_wait(10)
   soup = BeautifulSoup(driver.page_source, 'html.parser')
   first_header = soup.find('main')
   pageContainers= first_header.find_all('p', class_='pagination-result-text mb-auto d-flex justify-content-end')
   
   if pageContainers:
       for items in pageContainers:
            match = re.search(r'\d+(?=\s*result)', items.text.strip())
            numOfPages = int(match.group()) if match else f"No pages! {city}"
            if type(numOfPages) is int:
                numOfPages= math.ceil(numOfPages/20.0)
            else:
                continue
            print(f"{city}: Total pages: {numOfPages}")
            data_dict = {}

            #Total count done, start loading urls with names and page numbers
            for num in range(1, numOfPages + 1):
                webUrlForGettingData = f"https://registration.crpo.ca/mpower/mpp/member-directory-search.action?s={city}&n={num}"

                driver.get(webUrlForGettingData)
                print(f'{city}: Page Num: {num}')
                driver.implicitly_wait(10)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                main_section = soup.find('main')
                link_containers = main_section.find_all('a', class_='text-dark')
                link_list = []

                try:
                    for profile_links in link_containers:
                        hrefs = profile_links['href'].strip()
                        link_list.append(hrefs)
                except:
                    print("links were not extracted!")

                for link in link_list:
                    gettingMemberInfoURL = f"https://registration.crpo.ca/mpower/mpp/{link}"
                    stringUrl=driver.current_url
                    driver.get(gettingMemberInfoURL)
                    driver.implicitly_wait(20)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    main_section = soup.find('main')
                    try:
                        profile_containers = main_section.find_all('div', class_='profile-container')
                        Keepup = True
                        for profile_container in profile_containers:
                            data = {}
                            name_row = profile_container.find('div', class_='row mb-2')
                            if name_row and name_row != "":
                                name = name_row.find('h2').text.strip()
                                data["Name"] = name

                            rows = profile_container.find_all('div', class_='row')
                            for row in rows[1:]:
                                label = row.find('label', class_='col-sm-4 col-form-label fw-bold')
                                value = row.find('div', class_='col-sm-8 col-form-label')

                                if label and value:
                                    label_text = label.text.strip()
                                    value_text = value.text.strip()

                                    if value.find('a'):
                                        value_text = value.find('a').text.strip()

                                    data[label_text] = value_text
                            #TODO use Keepup Bool to filter results more!
                            if Keepup==True:
                                    address = profile_container.find('td', text="Canada")
                                    if address:
                                        try:
                                            address_th = address.find_parent().text.strip()
                                            
                                            try:
                                                data["Name of Clinic/Employer"] = address_th.split('\n')[0].strip()
                                            except IndexError:
                                                pass

                                            try:
                                                data["Address"] = address_th.split('\n')[1].strip()
                                            except IndexError:
                                                pass

                                            try:
                                                data["City"] = address_th.split('\n')[2].strip()
                                            except IndexError:
                                                pass

                                            try:
                                                data["Province"] = address_th.split('\n')[3].strip()
                                            except IndexError:
                                                pass

                                            try:
                                                data["Postal Code"] = address_th.split('\n')[4].strip()
                                            except IndexError:
                                                pass

                                            try:
                                                data["Country"] = address_th.split('\n')[5].strip()
                                            except IndexError:
                                                pass

                                            try:
                                                data["Phone"] = address_th.split('\n')[6].strip()
                                            except IndexError:
                                                pass

                                        except AttributeError:
                                            print(f"Error: Address information not found for {name}")

                                    if name in data_dict:
                                        data_dict[name].update(data)
                                    else:
                                        data_dict[name] = data
                    except:
                        print(f"profile not found! {stringUrl}")
            #if pages found:
            if numOfPages!=0:                        
                data_dict = {k: v for k, v in data_dict.items() if any(v.values())}
                print('data added!')
                with open(f'{city}Output.json', 'w') as json_file:
                    json.dump(data_dict, json_file, indent=2)

                df = pd.DataFrame(list(data_dict.values()))
                df = df[(df["Status"] == "Authorized to practise while working toward independent practice") | (df["Status"] == "Authorized to practise as a Qualifying registrant")]
                newKey = city.replace('%20','')
                os.makedirs('RawData', exist_ok=True)
                df.to_excel(f'RawData\{newKey}Output.xlsx', index=False)
                json_file_path = f'{city}Output.json'
                os.remove(json_file_path)
                print(f"Data saved in Excel for {city}.")
            else:
                print(f'No entries in this city : {city}')
print('program completed - closing driver')
driver.quit()
