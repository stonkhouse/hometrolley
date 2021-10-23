from logging import error
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import os
from os.path import join, dirname
from dotenv import load_dotenv
import time 
import traceback

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

POSTAL_CODE = os.environ.get("POSTAL_CODE")
ADDRESS = os.environ.get("ADDRESS")
ESTATE_NAME = os.environ.get("ESTATE_NAME")


# TODO: Move constants to separate file
LOGIN_CLASS = "jBOKcC"
GOOGLE_SIGN_IN_BUTTON = "Lixbv"
GOOGLE_EMAIL_INPUT = "whsOnd"

CLASS_POSTAL_CODE_BUTTON = "VhypV"
CLASS_POSTAL_CODE_INPUT = "hrYVGw"
CLASS_SELECT_ADDRESS = "jiKreI"
CSS_SELECTOR_SAVANNAH_SUGGESTION = 'span.main-text'
CSS_SELECTOR_SAVANNAH_SUGGESTION_SECONDARY = 'span.secondary_text'
CLASS_VERIFY_POSTAL_CODE = "cWDwbj" # SPAN

CLASS_OUT_OF_STOCK_SPAN = "gGWxuk"
CLASS_ADD_TO_CART_SPAN = "sc-1bsd7ul-1" #SPAN#applies for both  add to cart and out of stock
CLASS_ADD_TO_CART_BUTTON = "diHln"
# CLASS_ADD_TO_CART_SUCCESS = "XGqBZ" # span that should contain "added to cart"
CLASS_ADD_TO_CART_SUCCESS_DIV = "fDyoGf"
CLASS_PRODUCT_TITLE = "djlKtC"
CLASS_BUTTON = "hXOTht"  #DIV #applies for both  add to cart and out of stock
CLASS_NOT_AVAILABLE_NOW_TEXT = "kakvVu"
CLASS_NOT_AVAILABLE_CANCEL_SPAN = "kGdmdF"
CLASS_404_ERROR_SPAN = "hnTBMX"




def input_address():

    # 1. Click on postal code button 
    postal_code_button = driver.find_element_by_class_name(CLASS_POSTAL_CODE_BUTTON)
    postal_code_button.click()

    # 2. Input postal code
    driver.implicitly_wait(10)
    postal_code_input = driver.find_element_by_class_name(CLASS_POSTAL_CODE_INPUT)
    postal_code_input.send_keys(ADDRESS)

    # 3. Select the suggestion
    # main_selection = wait(driver, 900).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, CSS_SELECTOR_SAVANNAH_SUGGESTION), "SAVANNAH CONDOPARK"))
    # element = driver.find_element_by_css_selector(CSS_SELECTOR_SAVANNAH_SUGGESTION)
    location_suggestion = wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{ESTATE_NAME}']")))
    location_suggestion.click()

    # 4. Confirm the address 
    select_address_button  = wait(driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME, CLASS_SELECT_ADDRESS)))
    select_address_button.click()




out_of_stock_items = []
not_available_now_items = []
successful_items = []
error_items = [] 

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
        if (i != 1):
            print ("\n")
            print("Refreshing to get latest cart...")
            driver.refresh()

        try:
            driver.implicitly_wait(0)
            add_to_cart_div = driver.find_element_by_class_name("hXOTht")

            try:
                print ("Checking if in stock...")

                # add_to_cart_span = wait(driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, CLASS_ADD_TO_CART_SPAN), "Add to cart"))
                # add_to_cart_span = add_to_cart_div.find_element_by_class_name(CLASS_ADD_TO_CART_SPAN)
                add_to_cart_span = wait(add_to_cart_div, 1).until(EC.presence_of_element_located((By.CLASS_NAME, CLASS_ADD_TO_CART_SPAN)))
                # add_to_cart_span = wait(driver,10).until(EC.element_to_be_clickable)
                if add_to_cart_span.text == "Add to cart":
                    add_to_cart_button  = driver.find_element_by_class_name(CLASS_ADD_TO_CART_BUTTON)
                    product_title = driver.find_element_by_class_name(CLASS_PRODUCT_TITLE)
                    
                    # Add the item to the cart
                    add_to_cart_button.click()
                    try: 
                        # Wait for confirmation message 

                        print ("Finding confirmation message...")
                        wait(driver, 2, 0.2).until(EC.presence_of_element_located((By.CLASS_NAME, CLASS_ADD_TO_CART_SUCCESS_DIV)))
                        print (f"{product_title.text} IS available now :) ")

                        # wait(driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, CLASS_ADD_TO_CART_SUCCESS), "added to cart"))
                        print(f"Added to cart successfully: {product_title.text}")
                        successful_items.append(product_title.text)

                    except TimeoutException:
                        # Means we couldn't find the confirmation message , might be due to 
                        # 1) Not available now ...

                
                        # Handle edge case (Item not available , need more time)
                        wait(driver, 2).until(EC.text_to_be_present_in_element((By.CLASS_NAME, CLASS_NOT_AVAILABLE_NOW_TEXT), 'need more time'))
                        print (f"{product_title.text} NOT available now.")


                        cancel_not_available_item = driver.find_element_by_class_name(CLASS_NOT_AVAILABLE_CANCEL_SPAN)
                        cancel_not_available_item.click()
                        not_available_now_items.append(product_title.text)


                            

                    
                else:
                    # If item is out of stock
                    out_of_stock_span = driver.find_element_by_class_name(CLASS_OUT_OF_STOCK_SPAN)
                    if out_of_stock_span:
                        product_title = driver.find_element_by_class_name(CLASS_PRODUCT_TITLE)
                        print(f"Item is out of stock: {product_title.text}")
                        out_of_stock_items.append(product_title.text)

            except Exception:
                traceback.print_exc()

        except NoSuchElementException:
            # Check if got 404, if have just break
            print ("404 encountered")
            # wait(driver, timeout=0.5).until(EC.text_to_be_present_in_element((By.CLASS_NAME, CLASS_404_ERROR_SPAN), "can't seem to find"))
            error_items.append(driver.current_url)
            continue 
        except Exception:
            print (traceback.print_exc())
           
        
        
driver = webdriver.Chrome('/usr/local/bin/chromedriver')
url = "https://www.fairprice.com.sg/"
driver.get(url)


input_address()
print("Waiting for postal code to update... ")
wait(driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, CLASS_VERIFY_POSTAL_CODE), POSTAL_CODE))

add_items(get_grocery_list())
print("\n")
print ("-------- SUMMARY OF RUN --------")
print (f"Successful Items: {successful_items} , Count: {len(successful_items)}")
print (f"Out of Stock Items: {out_of_stock_items}, Count: {len(out_of_stock_items)}")
print (f"Unavailable Now Items: {not_available_now_items}, Count: {len(not_available_now_items)}")
print (f"Error Items: {error_items}, Count: {len(error_items)}")



