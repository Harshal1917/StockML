from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Selenium WebDriver
driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH
driver.get("https://www.nseindia.com/get-quotes/derivatives?symbol=INFY")

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='All Historical Data']"))).click()

# Click on "1Y"
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='1Y']"))).click()

# Set the date range (from and to)
# Adjust the XPaths based on the actual structure of the page
from_date = driver.find_element(By.XPATH, "//input[@placeholder='From']")
to_date = driver.find_element(By.XPATH, "//input[@placeholder='To']")
from_date.clear()
from_date.send_keys("01-01-2023")  # Set your desired from date
to_date.clear()
to_date.send_keys("31-12-2023")  # Set your desired to date

# Click on Filter (handle glitch if necessary)
driver.find_element(By.XPATH, "//button[text()='Filter']").click()
time.sleep(2)  # Wait for the filter to apply

# Select Instrument Type: "Stock Option"
instrument_type = driver.find_element(By.XPATH, "//select[@id='instrumentType']")
instrument_type.click()
instrument_type.find_element(By.XPATH, "//option[text()='Stock Option']").click()

# Select Year
year_selector = driver.find_element(By.XPATH, "//select[@id='year']")
year_selector.click()
year_selector.find_element(By.XPATH, "//option[text()='2023']").click()

# Select Expiry Date (you may need to loop through available expiry dates)
expiry_date_selector = driver.find_element(By.XPATH, "//select[@id='expiryDate']")
expiry_date_selector.click()
expiry_date_selector.find_element(By.XPATH, "//option[text()='Select Expiry Date']").click()  # Adjust as needed

# Click on Filter again
driver.find_element(By.XPATH, "//button[text()='Filter']").click()
time.sleep(2)  # Wait for the filter to apply

# Download the CSV
download_button = driver.find_element(By.XPATH, "//button[text()='Download (.csv)']")
download_button.click()

# Wait for the download to complete (you may need to adjust this)
time.sleep(5)

# Close the driver
driver.quit()


# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# # URL for the specific symbol (INFY) for the year 2023
# url = "https://www.nseindia.com/get-quotes/derivatives?symbol=INFY"

# # Set headers to mimic a browser visit
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Accept-Language': 'en-US,en;q=0.9',
# }

# response = requests.get(url, headers=headers)

# # Check if the request was successful
# if response.status_code == 200:
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Extract relevant data (adjust selectors based on actual HTML structure)
#     data = []
#     rows = soup.find_all('div', class_='your-row-class')  # Replace with actual class name for rows
#     for row in rows:
#         date = row.find('div', class_='date-class').text  # Replace with actual class name for date
#         open_price = row.find('div', class_='open-class').text  # Replace with actual class name for open price
#         high_price = row.find('div', class_='high-class').text  # Replace with actual class name for high price
#         low_price = row.find('div', class_='low-class').text  # Replace with actual class name for low price
#         close_price = row.find('div', class_='close-class').text  # Replace with actual class name for close price
        
#         # Append the extracted data to the list
#         data.append({
#             'Date': date,
#             'Open': open_price,
#             'High': high_price,
#             'Low': low_price,
#             'Close': close_price
#         })

#     # Create a DataFrame and save as CSV
#     df = pd.DataFrame(data)
#     print(df)
#     df.to_csv('INFY_derivatives_2023.csv', index=False)
#     print("Data saved to INFY_derivatives_2023.csv")
# else:
#     print(f"Failed to retrieve data: {response.status_code}")