# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Importing required libraries.
print('\n# Importing required libraries.')

import json, sys, os
import pandas as pd
from time import sleep
from pytz import timezone
from dotenv import load_dotenv
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Load environment variables from .env file.

# load_dotenv()     # uncomment this line to run locally

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
print('- '*25)
print('CLUBFEAST_USER_EMAIL:', os.environ.get('_CLUBFEAST_USER_EMAIL'), flush=True)
print('CLUBFEAST_USER_PASSWORD:', os.environ.get('_CLUBFEAST_USER_PASSWORD'), flush=True)
print('\n8X8_USER_USERNAME:', os.environ.get('_8X8_USER_USERNAME'), flush=True)
print('8X8_USER_PASSWORD:', os.environ.get('_8X8_USER_PASSWORD'), flush=True)
print('\nORDERS_REGION:', os.environ.get('ORDERS_REGION'), flush=True)
print('- '*25)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Setting up selenium driver.

print('\n# Setting up selenium driver.', flush=True)

driver_url = 'http://localhost:4444'

print(f'\n-> driver_url: {driver_url}', flush=True)

sleep(10)

chrome_options = webdriver.ChromeOptions()
chrome_options.page_load_strategy = 'normal'
chrome_options.add_argument("--start-maximized")
driver = webdriver.Remote(
    command_executor=driver_url,
    options=chrome_options
)
    
sleep(10)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Setting up user data and urls.
print('\n# Setting up user data and urls.', flush=True)

_clubfeast_data = {
        "user_email": os.environ.get('_CLUBFEAST_USER_EMAIL'),
        "user_password": os.environ.get('_CLUBFEAST_USER_PASSWORD'),
        "url_signin": "https://www.clubfeast.com/admins/sign_in",
}

_8x8_data = {
    "user_username": os.environ.get('_8X8_USER_USERNAME'),
    "user_password": os.environ.get('_8X8_USER_PASSWORD'),
    "user_number_temp": "(208) 696-1679",
    "user_number_clubfeast": "(707) 653-0716",
    "url_signin": "https://sso.8x8.com/v2/login",
    "url_messages": "https://work.8x8.com/conversations",
}

if os.environ.get('ORDERS_REGION') == 'EAST':
    _clubfeast_data["url_orders"] = "https://www.clubfeast.com/admin/order_track?all=true&model_name=order_track&scope=america_new_york_lunch_today_orders"    # EAST COAST LUNCH
elif os.environ.get('ORDERS_REGION') == 'WEST':
    _clubfeast_data["url_orders"] = "https://www.clubfeast.com/admin/order_track?all=true&model_name=order_track&scope=america_los_angeles_lunch_today_orders" # WEST COAST LUNCH
else:
    sys.exit('! ORDERS_REGION not found.')

_table_fields = {
    "package_field": "Package",
    "confirmation_status_field": "Status",
    "email_statuses_field": "Email Statuses",
    "restaurant_field": "Restaurant",
    # "dispatcher_field": "Dispatcher",
    "order_type_field": "Type",
    "pickup_time_field": "Pickup Time",
    # "while_glove_field": "Wg",
    # "vip_field": "Vip",
    "restaurant_cell_phone_field": "Cell",
    "restaurant_phone_number_field": "Phone",
    "order_id_field": "Order",
    "user_full_name_field": "Customer",
    "route_region_field": "Route Region",
    "num_of_dishes_field": "# Dishes",
    "num_of_family_meals_field": "# Family Meals",
    "orders_on_route_field": "# Orders On Route",
    "dish_lines_field": "Meal",
    "date_field": "Date",
    "time_zone_field": "Time Zone",
    "restaurant_emails_field": "Restaurant Emails",
    # "email_logs_field": "Email Logs",
    # "otter_confirmed_field": "Otter Confirmed"
}

_timezones = {
    'EST': 'EST5EDT',
    'PST': 'PST8PDT',
    'EAST': 'EST5EDT',
    'WEST': 'PST8PDT',
}

reminder_time_in_secs = 45*60

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Check if orders data file exists then load that data else scrap from clubfeast.

region_name = os.environ.get('ORDERS_REGION')
timezone_name = _timezones[region_name]
orders_file_name = f"{('_'.join((str(datetime.now(timezone(timezone_name)))).split()[0].split('-')))}_{region_name.title()}_Coast_Lunch_Orders"
orders_data_file_path = f"./data/{orders_file_name}.xlsx"

if os.path.isfile(orders_data_file_path):
    print(f'\n# Loading data from: {orders_data_file_path}', flush=True)
    orders_data_df = pd.read_excel(orders_data_file_path)
else:
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # Scraping orders data from clubfeast.
    print(f'\n# Scraping orders data for {(os.environ.get("ORDERS_REGION")).title()} Coast Lunch from clubfeast.', flush=True)

    driver.get(_clubfeast_data['url_orders'])

    if driver.current_url == _clubfeast_data['url_signin']:
        element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="admin_email"]')))).send_keys(_clubfeast_data["user_email"])
        element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="admin_password"]')))).send_keys(_clubfeast_data["user_password"])
        element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="new_admin"]/div[3]/div[1]/div')))).click()
        element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="new_admin"]/div[4]/input')))).click()

        print('\n# Signing in to the club feast.', flush=True)

    table_soup = None
    if driver.current_url == _clubfeast_data['url_orders']:
        element_orders = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        table_soup = BeautifulSoup(element_orders.get_attribute('innerHTML'), 'html.parser')
    else:
        sys.exit('! Url not found.')

    scraped_data = []
    for tr in table_soup.tbody.contents:
        if tr.name is not None:
            tr_data = {}
            for td in tr.contents:
                if td.name is not None:
                    field = [field for field in td['class'] if (('field' in field) and (field in _table_fields.keys()))]
                    if field:
                        tr_data[field[0]] = td.get_text().strip()
            if tr_data['confirmation_status_field'].lower() not in ['cancelled', 'not sent', 'delivered']:
                scraped_data.append(tr_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # Creating pandas dataframe and pre-processing data.
    print('\n# Creating pandas dataframe and pre-processing data.', flush=True)

    scraping_df = pd.DataFrame(scraped_data)
    scraping_df['reminder_message_status'] = ['scheduled' for x in range(len(scraping_df.index))]
    scraping_df.sort_values(by=['date_field', 'pickup_time_field'], inplace=True)
    scraping_df.reset_index(drop=True, inplace=True)
    scraping_df.to_excel(orders_data_file_path)
    orders_data_df = scraping_df.copy()
    print(f'\n# Saved data to: {orders_data_file_path}', flush=True)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

print('- '*27, flush=True)
print(f"Here's a list of today's {len(orders_data_df.index)} orders and their reminder message statuses.\n", flush=True)
for x in list(orders_data_df.index):
    print(
        f"{x:02d}. {orders_data_df.loc[x, 'package_field']} will be picked up at {orders_data_df.loc[x, 'pickup_time_field']} | Reminder Message Status: {orders_data_df.loc[x, 'reminder_message_status']}", 
        flush=True
    )
print('- '*27, flush=True)

# sys.exit('-> testing...')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Scheduling the reminder messages and sending them.
print(f'\n# Scheduling the reminder messages for {len(list(orders_data_df.index))} orders and sending them.', flush=True)

driver.get(_8x8_data["url_messages"])

# If the user is not signed in to 8x8 then sign in.
if driver.current_url == _8x8_data["url_signin"]:
    print('\n# Signing in to the 8x8.', flush=True)
    # 
    # Signing in to the 8x8.
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="loginId"]')))).send_keys(_8x8_data["user_username"] + Keys.ENTER)
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="rememberMe"]')))).click()
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="password"]')))).send_keys(_8x8_data["user_password"] + Keys.ENTER)
    # 
    # Closing dialogs after signing in.
    sleep(20)
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="___reactour"]/div[4]/div/button')))).click()
    sleep(5)
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="root"]/div/div[4]/div[2]/div/div/button[2]')))).click()
    sleep(5)
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="root"]/div/div[4]/div[2]/div[2]/button[1]')))).click()
    sleep(5)
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('#root > div > div.sc-jUEmfL.itFCsC > div.sc-gsxoIA.fkaZtB > svg > g > path')))).click()
    sleep(5)

for x in list(orders_data_df.index):
    _dt = (orders_data_df.loc[x, 'date_field'].split('-'))+(orders_data_df.loc[x, 'pickup_time_field'][:8].split(':'))+([orders_data_df.loc[x, 'time_zone_field']])
    pickup_datetime = timezone(_timezones[_dt[6]]).localize(datetime(year=int(_dt[0]), month=int(_dt[1]), day=int(_dt[2]), hour=int(_dt[3]), minute=int(_dt[4]), second=int(_dt[5])))
    current_datetime = datetime.now(timezone(_timezones[_dt[6]]))
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    print('- '*27, flush=True)
    print(f'{x:02d}.', orders_data_df.loc[x, "package_field"], flush=True)
    print('\n', flush=True)
    print(f'-> Pickup Datetime: {pickup_datetime}', flush=True); sleep(1)
    print(f'-> Current Datetime: {current_datetime}', flush=True); sleep(1)
    print('- '*27)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    
    # if pickup_time of next order is already passed then move to the next order...
    if current_datetime > pickup_datetime:
        print(f'\n! Skipping the reminder message for {orders_data_df.loc[x, "package_field"]}.\n', flush=True)
        if orders_data_df.loc[x, 'reminder_message_status'] == 'scheduled':
            orders_data_df.loc[x, 'reminder_message_status'] = 'not sent - skipped'
            orders_data_df.to_excel(orders_data_file_path)
            print(f"\n# Setting the reminder message status to 'not sent - skipped'.", flush=True)
            print(f'\n# Saved data to: {orders_data_file_path}', flush=True)
        
        continue

    # if pickup_time of next order is more than reminder time then put it to sleep...
    next_order_in_secs = ((pickup_datetime - datetime.now(timezone(_timezones[_dt[6]]))).total_seconds())
    if next_order_in_secs > reminder_time_in_secs:
        print('\n', flush=True)
        while True:
            next_order_in_secs = ((pickup_datetime - datetime.now(timezone(_timezones[_dt[6]]))).total_seconds())
            _sleep_time = next_order_in_secs-reminder_time_in_secs
            if _sleep_time > 60:
                td_message = str(timedelta(seconds=int(next_order_in_secs-reminder_time_in_secs))).split(':')
                print(f'! {td_message[0] + " Hours " if int(td_message[0]) > 0 else ""}{td_message[1]} Minutes {int(td_message[2])} Seconds remaining to send reminder message for {orders_data_df.loc[x, "package_field"]}.', flush=True)
                driver.current_url
                sleep(60)
            else:
                break

    # if pickup_time of next order is more than half the reminder time then put it to sleep...
    next_order_in_secs = ((pickup_datetime - datetime.now(timezone(_timezones[_dt[6]]))).total_seconds())
    if next_order_in_secs > (reminder_time_in_secs/2):
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
        # If 8x8 message page is not open then open it.
        if _8x8_data["url_messages"] not in driver.current_url:
            driver.get(_8x8_data["url_messages"])

        # If the user is not signed in to 8x8 then sign in.
        if driver.current_url == _8x8_data["url_signin"]:
            print('\n# Signing in to the 8x8.', flush=True)

            # Signing in to the 8x8.
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="loginId"]')))).send_keys(_8x8_data["user_username"] + Keys.ENTER)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="rememberMe"]')))).click()
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="password"]')))).send_keys(_8x8_data["user_password"] + Keys.ENTER)

            # Closing dialogs after signing in.
            sleep(3)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="___reactour"]/div[4]/div/button')))).click()
            sleep(3)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="root"]/div/div[4]/div[2]/div/div/button[2]')))).click()
            sleep(3)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="root"]/div/div[4]/div[2]/div[2]/button[1]')))).click()
            sleep(3)
            element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('#root > div > div.sc-jUEmfL.itFCsC > div.sc-gsxoIA.fkaZtB > svg > g > path')))).click()
            sleep(3)
            
        # If 8x8 message page is open then send reminder message.
        if _8x8_data["url_messages"] in driver.current_url:
            print(f'\n# Sending reminder for {orders_data_df.loc[x, "package_field"]}. x: {x}\n', flush=True)

            if orders_data_df.loc[x, 'reminder_message_status'] == 'scheduled' and str((orders_data_df.loc[x, 'restaurant_cell_phone_field'])).split(',')[0] != '-':
                order_data = json.loads(orders_data_df.loc[x].to_json())
                _message = f"Hi! This is Muaz from Club Feast Restaurants Operations.\n\nI just wanted to remind you about an order for today's Lunch as it will be picked up in the next 45 minutes.\n\nBelow are the order details;\n- Restaurant Name: {orders_data_df.loc[x, 'restaurant_field']}\n- Order Number: {order_data['package_field'][9:]}\n- Customer Name: {order_data['user_full_name_field']}\n- Pickup Time: {order_data['pickup_time_field']}\n- Meal Details: {order_data['dish_lines_field']}\n\nThank You!"

                # Sending reminder message to the restaurant.
                send_message_to = str((orders_data_df.loc[x, 'restaurant_cell_phone_field'])).split(',')[0]
                element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="root"]/div/div/div[3]/div[2]/button')))).click()
                element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="root"]/div/div/div[3]/div[2]/div[2]/div/div/div[2]/button')))).click()
                element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('#root > div > div.sc-jUEmfL.itFCsC > div.sc-gsxoIA.bITjmy > div > div > div.sc-fIYNhG.bKqzGN > div > div > input')))).send_keys(send_message_to)
                element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, ('//*[@id="root"]/div/div[4]/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/ol/li[1]/div/div/div[2]/div[1]/div/div/span')))).click()
                sleep(5)
                element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('#root > div > div > div.sc-iciGqv.cKHRza > div.sc-dbGSci.eDoklR > div > div > div > div.sc-hXvPvl.fcnLga > div > div.sc-VhHcL.efQveT > div > div > div.DraftEditor-editorContainer > div > div > div > div'))))
                for text in _message.split('\n'):
                    element.send_keys(text)
                    element.send_keys(Keys.SHIFT + Keys.ENTER)
                    print(text, flush=True)
                element.send_keys(Keys.ENTER)

                sleep(2)

                orders_data_df.loc[x, 'reminder_message_status'] = 'sent'
                orders_data_df.to_excel(orders_data_file_path)
                print(f"\n# Setting the reminder message status to 'sent'.", flush=True)
                print(f'\n# Saved data to: {orders_data_file_path}', flush=True)

                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
                print('\n', flush=True)
                print(
                    f"> Reminder Sent,\n",
                    f" - package      : {orders_data_df.loc[x, 'package_field']}\n",
                    f" - status       : {orders_data_df.loc[x, 'confirmation_status_field']}\n",
                    f" - restaurant   : {orders_data_df.loc[x, 'restaurant_field']}\n",
                    f" - cell_phone   : {orders_data_df.loc[x, 'restaurant_cell_phone_field']}\n",
                    f" - phone_number : {orders_data_df.loc[x, 'restaurant_phone_number_field']}\n",
                    f" - pickup_time  : {orders_data_df.loc[x, 'pickup_time_field']}\n",
                    f" - pickup_date  : {orders_data_df.loc[x, 'date_field']}\n",
                    f" - time_zone    : {orders_data_df.loc[x, 'time_zone_field']}\n",
                    f" - customer     : {orders_data_df.loc[x, 'user_full_name_field']}\n",
                    f" - sent_at      : {datetime.now(timezone(_timezones[_dt[6]]))}", flush=True
                )
                print('* '*85, flush=True)

            elif orders_data_df.loc[x, 'reminder_message_status'] == 'scheduled' and str((orders_data_df.loc[x, 'restaurant_cell_phone_field'])).split(',')[0] == '-':
                orders_data_df.loc[x, 'reminder_message_status'] = 'not sent - cell number missing'
                orders_data_df.to_excel(orders_data_file_path)
                print(f"\n# Setting the reminder message status to 'not sent - cell number missing'.", flush=True)
                print(f'\n# Saved data to: {orders_data_file_path}', flush=True)

    else:
        print(f'\n! Skipping the reminder message for {orders_data_df.loc[x, "package_field"]}.\n', flush=True)

driver.close()
driver.quit()