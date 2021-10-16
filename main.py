from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import os
from os.path import join, dirname
from dotenv import load_dotenv
import time 

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


POSTAL_CODE = os.environ.get("POSTAL_CODE")
ADDRESS = os.environ.get("ADDRESS")


# TODO: Move constants to separate file
LOGIN_CLASS = "jBOKcC"
GOOGLE_SIGN_IN_BUTTON = "Lixbv"
GOOGLE_EMAIL_INPUT = "whsOnd"

CLASS_POSTAL_CODE_BUTTON = "VhypV"
CLASS_POSTAL_CODE_INPUT = "hrYVGw"
CLASS_SELECT_ADDRESS = "jiKreI"
CSS_SELECTOR_SAVANNAH_SUGGESTION = 'span.main-text'
CLASS_VERIFY_POSTAL_CODE = "cWDwbj" # SPAN

OUT_OF_STOCK_SPAN = "gGWxuk"
ADD_TO_CART_SPAN = "iKyLRU" #SPAN#applies for both  add to cart and out of stock
CLASS_ADD_TO_CART_SUCCESS = "fDyoGf"
CLASS_PRODUCT_TITLE = "djlKtC"
CLASS_BUTTON = "hXOTht"  #DIV #applies for both  add to cart and out of stock





def input_address():

    # 1. Click on postal code button 
    postal_code_button = driver.find_element_by_class_name(CLASS_POSTAL_CODE_BUTTON)
    postal_code_button.click()

    # 2. Input postal code
    driver.implicitly_wait(10)
    postal_code_input = driver.find_element_by_class_name(CLASS_POSTAL_CODE_INPUT)
    postal_code_input.send_keys(ADDRESS)

    wait(driver, 900).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, CSS_SELECTOR_SAVANNAH_SUGGESTION), "SAVANNAH CONDOPARK"))
    element = driver.find_element_by_css_selector(CSS_SELECTOR_SAVANNAH_SUGGESTION)
    element.click()

    select_address_button  = wait(driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME, CLASS_SELECT_ADDRESS)))
    select_address_button.click()




out_of_stock_items = []
successful_items = []

def get_grocery_list():
    my_file = open("grocery_links.txt", "r")
    content = my_file.read()
    content_list = content.split("\n")
    my_file.close()
    print(content_list)
    return content_list


def open_new_tab(link):
    # driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    driver.execute_script("window.open('{}');".format(link))
    return 


# TODO: Handle 404 events
def add_items(list_of_item_links):
    for link in list_of_item_links:
        open_new_tab(link)

    for i in range(1, len(driver.window_handles)):
        driver.switch_to.window(driver.window_handles[i])
        print("Refreshing to get latest cart...")
        driver.refresh()
        driver.implicitly_wait(5)

        try:
            add_to_cart_span = driver.find_element_by_class_name(ADD_TO_CART_SPAN)

            if add_to_cart_span:
                add_to_cart_span.click()
                product_title = driver.find_element_by_class_name(CLASS_PRODUCT_TITLE)
                
                wait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, CLASS_ADD_TO_CART_SUCCESS)))
                
                print(f"Added to cart successfully: {product_title.text}")
                successful_items.append(product_title.text)

                
            else:
                out_of_stock_span = driver.find_element_by_class_name(OUT_OF_STOCK_SPAN)
                if out_of_stock_span:
                    product_title = driver.find_element_by_class_name(CLASS_PRODUCT_TITLE)
                    print(f"Item is out of stock: {product_title.text}")
                    out_of_stock_items.append(product_title.text)

        except Exception as e:
            print (e)
        
        
driver = webdriver.Chrome('/usr/local/bin/chromedriver')
url = "https://www.fairprice.com.sg/"
driver.get(url)


input_address()
print("Waiting for postal code to update... ")
wait(driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, CLASS_VERIFY_POSTAL_CODE), POSTAL_CODE))

add_items(get_grocery_list())
print (f"Successful Items: {successful_items} , Count: {len(successful_items)}")
print (f"Out of Stock Items: {out_of_stock_items}, Count: {len(out_of_stock_items)}")



