from datetime import datetime as dt
import logging
import os
import time

from dotenv import load_dotenv
import psycopg
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_logger(logging: logging) -> None:
	"""
	Setup logger with function name identifier

		param:
			func_name (str): name of the function where the logger was executed
	"""
	logging.basicConfig(
		level=logging.DEBUG,
		format="{asctime} - ({filename}: {funcName}) -> {message}",
		style="{",
		datefmt="%Y-%m-%d %H:%m:%S"
	)

def provide_scraping_result_dict(
	web_url: str,
	is_gambling_site: bool,
	is_error: bool,
	scraped_elements: str,
	scraping_initiation_time: dt,
	exception_raised: str
) -> dict:
	"""
	Return scraping report as a dictionary
	
		params:
			web_url (str): URL of scraped website
			is_gambling_site (bool): whether the site is a gambling site or not
			is_error (bool): whether the scraping process on the URL encounters an error
			scraped_elements (str): HTML elements of the web as string
			scraping_initiation_time (datetime): datetime of the scraping initiation process
			exception_raised (str): exception raised
		
		return:
			dictionary containing the scraping report
	"""
	
	return {
		"web_url": web_url,
		"is_gambling_site": is_gambling_site,
		"is_error": is_error,
		"scraped_elements": scraped_elements,
		"scraping_initiation_time": scraping_initiation_time,
		"exception_raised": exception_raised
	}

def is_vertical_scrollbar_present(driver: webdriver) -> bool:
	"""
	Check whether the scrollbar present on the web page

		param:
			driver (webdriver): Selenium webdriver
		
		return:
			bool: whether scroll height > viewport height
	"""
	scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
	viewport_height = driver.execute_script("return document.documentElement.clientHeight")

	return scroll_height>viewport_height

def wait_until_page_ready(driver: webdriver) -> None:
	"""
	Command webdriver to wait until the the web page fully loaded (in ready state)

		param:
			driver (webdriver): Selenium webdriver
	"""

	WebDriverWait(driver, 30).until(
		lambda driver: driver.execute_script("return document.readyState")=="complete"
	)

def get_scraping_result(
	web_url: str, 
	is_gambling_site: bool, 
	driver: webdriver,
	df_row_count: int,
	item_position: int
) -> dict:
	"""
	Return scraping result as dictionary
		parameters:
			web_url (str): url of the web to scrape
			is_gambling_site (bool): whether the web a gambling site or not
			driver (webdriver): selenium webdriver
			item_position (int): position of the item in the dataframe, default=None
			df_row_count (int): count of dataframe rows, default=None

		return:
			dictonary containing scraping result \
			using :provide_scraping_result_dict:`provide_scraping_result_dict function`
	"""

	# set is_error to False to simplify value matching
	is_error = True

	scraped_elements = None
	exception_raised = None

	try:
		# some gambling webpage are loaded slowly
		# thus I use explicit wait function from selenium
		# to wait until the web page is loaded successfully wihtin defined interval in seconds
		#** if the page loaded before the max interval reached, it returns the element reference
		# and the code will continue executing futher scripts
		#** otherwise, it will raise timeout exception
		# this method more effective than using time.sleep function
		driver.get(web_url)
		wait_until_page_ready(driver)

		# suppose the driver returned the web's elements
		# there are some web page using verifying method to distinguish between human and bot (captcha)
		#** the captcha takes time to load and the interval varies
		# thus, I will wait using time.sleep function
		# before retrieve web page's elements
		time.sleep(5)

		# some web pages are having scrollbar to load all of its elements
		# to make sure all of the elements are loaded
		# I will scroll to the end of it if vertical scroll bar is present
		if(is_vertical_scrollbar_present(driver)):
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		time.sleep(5)

		scraped_elements = driver.page_source

		is_error=False
	except TimeoutException:
		exception_raised = "Timeout Exception"
		print("Error occurred: ", exception_raised)
	except Exception as e:
		exception_raised = e
		print(f"Error occurred: {e}")
	finally:
		print(f"[{item_position}/{df_row_count}] scraping finished on {web_url}")
		print("\tis error: ", is_error)
		print("\texception: ", exception_raised)

		return provide_scraping_result_dict(
			web_url=web_url,
			is_gambling_site=is_gambling_site,
			is_error=is_error,
			scraped_elements=scraped_elements,
			scraping_initiation_time=dt.now(),
			exception_raised=exception_raised
		)

def get_crawling_scraping_result(web_url: str, driver: webdriver) -> dict:
	"""
	Return scraping result from crawling as dictionary
		params:
			web_url (str): url of the web to scrape		
			driver (webdriver): selenium webdriver

		return:
			dictonary containing scraping result \
			using :provide_scraping_result_dict:`provide_scraping_result_dict function`
	"""

	# set is_error to False to simplify value matching
	is_error = True

	scraped_elements = None
	exception_raised = None

	try:
		# some gambling webpage are loaded slowly
		# thus I use explicit wait function from selenium
		# to wait until the web page is loaded successfully wihtin defined interval in seconds
		#** if the page loaded before the max interval reached, it returns the element reference
		# and the code will continue executing futher scripts
		#** otherwise, it will raise timeout exception
		# this method more effective than using time.sleep function
		wait_until_page_ready(driver)

		# suppose the driver returned the web's elements
		# there are some web page using verifying method to distinguish between human and bot (captcha)
		#** the captcha takes time to load and the interval varies
		# thus, I will wait using time.sleep function
		# before retrieve web page's elements
		time.sleep(5)

		# some web pages are having scrollbar to load all of its elements
		# to make sure all of the elements are loaded
		# I will scroll to the end of it if vertical scroll bar is present
		if(is_vertical_scrollbar_present(driver)):
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		time.sleep(5)

		scraped_elements = driver.page_source

		is_error=False
	except TimeoutException:
		exception_raised = "Timeout Exception"
		print("Error occurred: ", exception_raised)
	except NoSuchElementException:
		exception_raised = "The web is not loaded"
		print("Error occurred: ", exception_raised)
	except Exception as e:
		exception_raised = e
		print(f"Error occurred: {e}")
	finally:
		print(f"scraping finished on {web_url}")
		print("\tis error: ", is_error)
		print("\texception: ", exception_raised)

		return {
			"web_url": web_url,
			"is_error": is_error,
			"scraped_elements": scraped_elements,
			"scraping_initiation_time": dt.now(),
			"exception_raised": exception_raised
		}


def get_webdriver() -> webdriver:
	"""
	Set-up webdriver object with options

		return:
			Selenium webdriver object with defined options
	"""
	options = webdriver.ChromeOptions()
	# options.add_argument("--headless=new")
	options.add_argument('--disable-gpu')
	options.add_argument('--mute-audio')
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--allow-insecure-localhost')
	options.add_argument('--ignore-ssl-errors')
	options.add_argument('--log-level=3')
	options.add_argument('--disable-web-security')

	# install adblocker
	options.add_extension(os.path.abspath("adblock.crx"))

	driver = webdriver.Chrome(options=options)

	# By default, browser open new tab to show welcome page of new extension
	# This will make the crawler produce unexpected behaviour
	# To solve it, I will close the welcome tab
	WebDriverWait(driver, 120).until(EC.new_window_is_opened(driver.window_handles))

	#** closing the welcome page tab right after its detected as opened
	#** makes the driver open the page again
	# driver must wait a little while to make sure 
	# the welcome page fully loaded before close the tab
	# based on the observations, I will program the driver to wait
	# in a short time before closing the new tab
	time.sleep(3)

	driver.switch_to.window(driver.window_handles[1])
	driver.close()

	# switch back to first tab
	driver.switch_to.window(driver.window_handles[0])

	return driver