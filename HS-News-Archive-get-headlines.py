# This script automates a query into historic news articles and fetches headline data
# from Helsingin Sanomat news archive at https://www.hs.fi/arkisto/
# Only the headlines and their dates of publishing are returned.
# You can search for names, words etc to appear in the articles and select how many headlines you want returned

# IMPORTANT: Before running, read the README file for the disclaimer and for the general terms and
# conditions of Sanoma Media Finland. Use of this script is prohibited without first obtaining
# formal consent from Sanoma Media Finland.

# NOTE: There's one big issue with the website. When you load the last page of results,
# all results disappear. The only solution I've found to work is to first calculate
# the maximum number of 'acceptable' load more times and only then reload the pages
# and fetch the headline data.


# Import the required packages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd


# Start by typing in the search term you want to use (e.g. "koronavirus", "elon musk", "tekoäly")
search_term = input("Search term:\n")

# ... and how many articles you want to get returned
no_of_articles_wanted = int(input("How many headlines?\n"))

# Create a local WebDriver
path = "/Users/henrihapponen/chromedriver"
driver = webdriver.Chrome(path)

# Open the website of Helsingin Sanomat news archives
driver.get("https://www.hs.fi/arkisto/")

# Wait for the page to load
time.sleep(5)


# Accept cookies, haven't figured out how yet
# For now, has to be done manually when the website opens

# cookie_window = driver.window_handles
# driver.switch_to.window(str(cookie_window))

# cookies_ok_button = driver.find_element_by_xpath("/html/body/div/div[3]/div[3]/div[2]/div/button[2]")
# cookies_ok_button.click()


# Locate the search bar and date selection field
search_bar = driver.find_element_by_id("main-search")
time_select_menu = driver.find_element_by_id("search-time-select")
time_select = Select(time_select_menu)

# Send the search term into the search bar
search_bar.send_keys(search_term)

# Select the time frame
# For now we have to use "published any time" so no need to select further start and end dates

time_select.select_by_visible_text("Milloin tahansa")

# If we were to use "set start and end dates" (NOTE: not functional yet)
# time_select.select_by_visible_text("Oma aikaväli")

# Not sure how I could fix the start and end dates, these seem to be very tricky to work with
# date_picker = driver.find_element_by_class_name(
#   "jsx-3495263876 calendar-icon absolute pointer-events-none bg-center bg-contain bg-no-repeat")
# date_picker.click()

# start_date = driver.find_element_by_id("search-start-date")
# end_date = driver.find_element_by_id("search-end-date")

# These don't work, it's annoyingly close but the year doesn't quite work
# start_date.send_keys("2005-11-11")
# time.sleep(1)
# end_date.send_keys("01-01-2015")

# Send the query and load the first 'page' of results
search_bar.send_keys(Keys.RETURN)

# Wait for the results to load
time.sleep(3)


# Next we need to establish the maximum number of 'acceptable' load more times.
# This is done by counting each time we press of the load more button until the page crashes
# The following will press the 'Load More' button as long as it keeps appearing on the page
load_more_times = 0
while True:
    try:
        load_more_button = driver.find_element_by_xpath(
            "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/div/button")
        load_more_button.click()
        load_more_times += 1
        time.sleep(1)
    except NoSuchElementException:
        break

time.sleep(2)

# This is how many 'acceptable' load more times we are allowed in the actual run that will follow
acceptable_load_more_times = load_more_times - 1

# Quit the driver
driver.quit()

# Optional
print("Acceptable Load More times: " + str(acceptable_load_more_times))


# Now we repeat the query but use the 'Acceptable Load More Times'
# and also run the actual scraper.

# Create a local WebDriver (again)
path = "/Users/henrihapponen/chromedriver"
driver = webdriver.Chrome(path)

# Open the website of Helsingin Sanomat news archives (again)
driver.get("https://www.hs.fi/arkisto/")

# Wait for the page to load
time.sleep(5)

# Locate our search bar and date selection field
search_bar = driver.find_element_by_id("main-search")
time_select_menu = driver.find_element_by_id("search-time-select")
time_select = Select(time_select_menu)

# Search term is already set earlier so we can send that to the search bar
search_bar.send_keys(search_term)

# The same time frame issue applies, we have to use "published any time"
time_select.select_by_visible_text("Milloin tahansa")

# If we were to use "set start and end dates" (NOTE: not functional yet)
# time_select.select_by_visible_text("Oma aikaväli")

# Not sure how I could fix the start and end dates, these seem to be very tricky to work with
# date_picker = driver.find_element_by_class_name(
#   "jsx-3495263876 calendar-icon absolute pointer-events-none bg-center bg-contain bg-no-repeat")
# date_picker.click()

# start_date = driver.find_element_by_id("search-start-date")
# end_date = driver.find_element_by_id("search-end-date")

# These don't work, it's annoyingly close but the year doesn't work
# start_date.send_keys("2005-11-11")
# time.sleep(1)
# end_date.send_keys("01-01-2015")

# Send the query
search_bar.send_keys(Keys.RETURN)

time.sleep(3)

# Load all pages (except for the last one which makes all results disappear)
for i in range(acceptable_load_more_times):
    load_more_button = driver.find_element_by_xpath(
        "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/div/button")
    load_more_button.click()
    time.sleep(1)


# Now that all pages are loaded, next we fetch all the headlines and their dates of publishing
# and append our list with dictionaries for each entry.
# Have to use 'try' because there are a few different xpath patterns for the articles...

articles = []
article_num = 1

for i in range(no_of_articles_wanted):
    try:
        try:
            headline = driver.find_element_by_xpath(
                "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/article["
                + str(article_num) + "]/a/section/div[1]/div[2]/h2/span[2]").text
        except NoSuchElementException:
            try:
                headline = driver.find_element_by_xpath(
                    "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/article["
                    + str(article_num) + "]/a/section/div[1]/div[2]/h2/span").text
            except NoSuchElementException:
                try:
                    headline = driver.find_element_by_xpath(
                        "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/article["
                        + str(article_num) + "]/a/section/div[1]/div/h2/span[2]").text
                except NoSuchElementException:
                    headline = driver.find_element_by_xpath(
                        "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/article["
                        + str(article_num) + "]/a/section/div[1]/div/h2/span").text
        try:
            published_time = driver.find_element_by_xpath(
                "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/article["
                + str(article_num) + "]/a/section/div[2]/div[1]/time").get_attribute("datetime")
        except NoSuchElementException:
            published_time = driver.find_element_by_xpath(
                "/html/body/div[1]/div[2]/div[3]/div[1]/div[2]/main/section[4]/section/div[2]/section/article["
                + str(article_num) + "]/a/section/div[2]/div[2]/time").get_attribute("datetime")
        articles.append({"Article No": article_num, "Published": published_time, "Headline": headline})
        article_num += 1
    except NoSuchElementException:
        article_num += 1


# Then we read the data into a Pandas data frame
articles_df = pd.DataFrame(articles)

# Optional
print("Number of articles found: " + str(articles_df.shape[0]))

# Optional
print(articles_df.head())

# Create a csv file, and name it according to the search term
file_name = "HS Articles for " + search_term + ".csv"
articles_df.to_csv(file_name)

# Wait 10 seconds and quit the driver
time.sleep(10)
driver.quit()