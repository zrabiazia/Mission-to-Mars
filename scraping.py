# Import Splinter and BeautifulSoup 
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

def scrape_all():
    #initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)

    news_title, news_p = mars_news(browser)
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_urls": hemisphere_images_urls(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data
  
def mars_news(browser):
    # visit the Mars news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    #optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.side", wait_time=1)

    # HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    #add try/except for error handeling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        slide_elem.find("div", class_="content_title")
        #use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # use the parent element to find teh paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()    
    except AttributeError:
        return None, None

    return news_title, news_p
        

### Featured Image ###
def featured_image(browser):
    #visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()
    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    #add try/except for error handeling
    try:
        #find the relative image url
        img_url_rel= img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    try:
        # read table with pandas dataframe read_html- MARS FACTS
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    #assign columns and set index to DataFrame
    df.columns =['Description', 'Mars'] 
    df.set_index('Description', inplace=True)

    #from DataFrame to HTML
    return df.to_html(classes=" table table-striped")

# ### Mars Weather
def mars_weather():

    # Visit the weather website
    url = 'https://mars.nasa.gov/insight/weather/'
    browser.visit(url)
    # Parse the data
    html = browser.html
    weather_soup = soup(html, 'html.parser')
    try:
        # Scrape the Daily Weather Report table
        weather_table = weather_soup.find('table', class_='mb_table')
    except:
        return None
    return weather_table


# ### Hemispheres
def hemisphere_images_urls(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')
    hemisphere_image_urls = hemisphere_soup.find_all('div', class_='description', recursive=True)
    
    hemisphere_images_urls = []

    for hemisphere_image_url in hemisphere_image_urls:
        hemispheres = {}
        img_url_rel = hemisphere_image_url.find('a')['href']
        image_url = f'https://astrogeology.usgs.gov{img_url_rel}'
        browser.visit(image_url)
        html = browser.html
        hemisphere_soup = soup(html, 'html.parser')
        hemispheres['img_url'] = hemisphere_soup.select_one('div.downloads ul li a').get("href")
        hemispheres['title'] = hemisphere_soup.select_one('h2.title').get_text()
        hemisphere_images_urls.append(hemispheres)

    return hemisphere_images_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

