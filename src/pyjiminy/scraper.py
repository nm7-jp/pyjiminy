# -*- coding: utf-8 -*-
from posixpath import dirname
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotSelectableException, 
    ElementClickInterceptedException
)
from logging import getLogger, config
import yaml
import json
import datetime
from . import const as C
from pyfields import field, make_init
from .helper import get_env

# Tokyo disney resport site
C.URL = "https://reserve.tokyodisneyresort.jp/"

# Abbreviations
## DAH: Disney Ambassador Hotel
## DHM: tokyo Disney sea Hotel MIRACOSTA
## TDH: Tokyo Disney land Hotel
## DCH: tokyo disney Celebration Hotel
C.HOTEL_ALL = {"DAH","DHM","TDH","DCH"}

# Input limits in reservation site
## Maximum number of stay nights 
C.MAX_NIGHTS = 5
## Maximum number of rooms
C.MAX_ROOMS = 3
## Maximum number of adults
C.MAX_ADULTS= 15

# User Agent
C.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44"

# Format of arrival date 
C.DATE_FORMAT = "%Y/%m/%d"

with open(dirname(__file__) + "/yaml/config.yml") as f:
    config.dictConfig(yaml.safe_load(f))
logger = getLogger(__name__)


class HotelSearcher:
    """Search availability of Disney resort hotel and return the status of each room type

    Attributes:
        hotel (str): abbriviation of the hotel name
        year (int): year of staying at a hotel
        month (int): month of staying at a hotel
        day (int): day of staying at a hotel
        nights (int): number of nights stayed at a hotel
        rooms (int): number of rooms stayed at a hotel
        adults (int): number of adults stayed at a hotel
    """
    hotel:str = field(validators={f'hotel should be either of {",".join(list(C.HOTEL_ALL))}' : lambda hotel: hotel in C.HOTEL_ALL})
    year:str = field(check_type=True, doc='year must be str')
    month:str = field(check_type=True, doc='month must be str')
    day:str = field(check_type=True, doc='day must be str')
    nights:str = field(validators={f'nights should be less than {str(C.MAX_NIGHTS)}': lambda nights: int(nights) in range(1, C.MAX_NIGHTS) })
    rooms:str = field(validators={f'rooms should be less than {str(C.MAX_ROOMS)}': lambda rooms: int(rooms) in range(1, C.MAX_ROOMS) })
    adults:str = field(validators={f'adults should be less than {str(C.MAX_ADULTS)}': lambda adults: int(adults) in range(1, C.MAX_ADULTS) })    
    __init__ = make_init()

    def __initialize_driver_options(self) -> WebDriver:
        """Initialize chrome options of selenium web driver

        Returns:
            WebDriver: Selenium Web driver 
                        after configuring Chrome Options and target URL
        """
        options = webdriver.chrome.options.Options()

        if get_env() == "production":
            # To hide browser screen
            options.add_argument("--headless")

        options.add_argument('--no-sandbox')
        options.add_argument("--user-agent=" + C.USER_AGENT)

        # Store shared memory on /tmp instead of /dev/shm
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)

        driver.get(C.URL)
        driver.set_window_size('1200', '1000')
        
        return driver      

    def __execute_search(self) -> WebDriver:
        """Search hotel booking with given conditions

        Returns:
            WebDriver: Selenium Web driver after form submission under given conditions
        """        
        driver = self.__initialize_driver_options()

        try:
            # Extract each elements for search conditions
            hotel_category = driver.find_element(by=By.XPATH, value="//*[@id='content']/div[2]/div[2]/div/ul/li[2]/a/img")
            nights_dropdown = driver.find_element(by=By.XPATH, value="//select[@id='hotelStayDays']")
            rooms_dropdown = driver.find_element(by=By.XPATH, value="//select[@id='hotelRoomsNum']")
            adults_dropdown = driver.find_element(by=By.XPATH, value="//select[@id='hotelAdultNum']")
            submission = driver.find_element(by=By.XPATH, value="//*[@id='hotelFormId']/div/p/a/img")

            # Select hotel as a searched category
            hotel_category.click()

            # HACK: Use JQuery to input arbitrary arrival date
            #     : because the text cannot be directly inserted for some reseason
            d = datetime.date(int(self.year), int(self.month), int(self.day))
            date = d.strftime(C.DATE_FORMAT)  
            driver.execute_script("$('#hotelUseDate').datepicker('setDate',new Date('" + date + "'));")

            # Select stay nights from dropdown list
            nights_seleted = Select(nights_dropdown) 
            nights_seleted.select_by_value(self.nights)

            # Select number of rooms from dropdown list
            rooms_selected = Select(rooms_dropdown)
            rooms_selected.select_by_value(self.rooms)

            # Select number of adults from dropdown list
            adults_selected = Select(adults_dropdown)
            adults_selected.select_by_value(self.adults)

            # Start to search
            submission.click()
            
        except NoSuchElementException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()      
        except ElementNotSelectableException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()
        except ElementClickInterceptedException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()

        try:
            WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.XPATH,"//input[@name='js-hotelCdCheckBox'][@type='checkbox']")))
        except TimeoutException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()

        return driver
    
    def get_room_status(self) ->str:
        """Get availability of each hotel room type

        Returns:
            str: Room type, its price and availability with JSON schema
                    e.g.) [{"name": "DHM", "price": "50,000円", "is_available": true}]
        """
        driver = self.__execute_search()

        try:
            # Extract each elements in the page of search results
            hotel_checkboxes = driver.find_elements(by=By.XPATH, value="//input[@name='js-hotelCdCheckBox'][@type='checkbox']")
            hotel_labels = driver.find_elements(by=By.XPATH, value="//label")

        except NoSuchElementException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()      
        
        # HACK: Get the list of the hotels excluding target hotel to be searched
        #     : and only click the hotels not to be searched 
        #     : because "click" corresponds to "excluding the list from searching targets"
        excluded_hotels = set(C.HOTEL_ALL) - set(self.hotel.split())
        for c in hotel_checkboxes:
            for l in hotel_labels:
                if (c.get_attribute("id") == l.get_attribute("for")):
                    if (c.get_attribute("value") in excluded_hotels):
                        l.click()

        # Show all of the room status including full
        try:
            show_hotel_status  = driver.find_element(by=By.XPATH, value="//a[@href='#tabCont1']")
            show_hotel_status.click()
        except NoSuchElementException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()      
        except ElementNotSelectableException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()
        except ElementClickInterceptedException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit()        

        # Get elements including the type of the rooms
        try:
            room_elements =  driver.find_elements(by=By.XPATH, value="//div[contains(@id, 'section') and contains(@id, '"+ self.hotel + "')]")
        except NoSuchElementException as e:
            logger.exception('ERROR: %s', e)
            driver.close()
            driver.quit() 
            
        room_status = []

        for re in room_elements:

            dict = {}
    
            # FIXME: Use get_attribute("textContent") method 
            #      : invisible element cannot be obtained by us9ing text method
            #      : Specify index of array to find element because the elements
            #      : cannot be searched for some reasons when relative XPATH was specified
            try:
                dict["name"] = re.find_element(by=By.XPATH, value="./div[1]/div[2]/h3").get_attribute("textContent").strip()
                dict["price"] = re.find_element(by=By.XPATH, value="./div[1]/dl/dd").get_attribute("textContent").strip()
            except NoSuchElementException as e:
                logger.exception('ERROR: %s', e)
                driver.close()
                driver.quit()  

            # HACK: Check room availability by evaluating the value of 'class'
            #     : under the condition that the value includes 'full' in string 
            #     : in the case of full booking
            # 　　: e.g. "block ecTypeSection js-accordion  DHM full"
            dict["is_available"] = False if "full" in re.get_attribute('class') else True
    
            room_status.append(dict)

        driver.close()
        driver.quit()
        
        return json.dumps(room_status)