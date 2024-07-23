import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Initialize WebDriver
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--headless")  # Run in headless mode if desired

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL
paris_url = "https://www.parisianhome.com/appartements/"

# Launching the website
driver.get(paris_url)

# Scroll to load all properties
scroll_pause_time = 2  # Adjust the pause time if necessary
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Locate all property cards (adjust the XPath if necessary)
property_cards = driver.find_elements(By.XPATH, '')

# Extract URLs from the property cards
property_urls = [card.find_element(By.XPATH, ".//a").get_attribute('href') for card in property_cards]

# Remove any None values from the list
property_urls = [url for url in property_urls if url]

# Checking the number of URLs
print(f"Found {len(property_urls)} property URLs.")

# Helper function for safe text extraction
def safe_extract_text(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text
    except:
        return "N/A"

# Data Collection
paris_data = []

for url in property_urls:
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '')))
    except:
        continue

    property_name = safe_extract_text(driver, '')
    address = safe_extract_text(driver, '')
    price = safe_extract_text(driver, '')
    occupants = safe_extract_text(driver, '')
    floor = safe_extract_text(driver, '')
    arrondissement = safe_extract_text(driver, '')

    print(f"Property Name: {property_name}")
    print(f"Address: {address}")
    print(f"Price: {price}")
    print(f"Occupants: {occupants}")
    print(f"Floor: {floor}")
    print(f"Arrondissement: {arrondissement}")

    paris_data.append({
        "Property_Name": property_name,
        "Address": address,
        "Price": price,
        "Occupants": occupants,
        "Floor": floor,
        "Arrondissement": arrondissement,
    })

# Closing the driver
driver.quit()

# Creating dataframe
paris_df = pd.DataFrame(paris_data)

# Data cleaning
paris_df['Price'] = paris_df['Price'].str.replace("Price Upon Request", "0").str.replace("$", "").str.replace(",", "").astype(float)
paris_df['Occupants'] = paris_df['Occupants'].str.extract(r'(\d+)').astype(float)
paris_df['Floor'] = paris_df['Floor'].str.extract(r'(\d+)').astype(float)
paris_df['Arrondissement'] = paris_df['Arrondissement'].str.extract(r'(\d+)').astype(float)

# Exporting as CSV file
paris_df.to_csv("paris_sotheby_property_rental.csv", index=False)

# Display the dataframe
print(paris_df.head())
print("Data scraping completed and saved to paris_sotheby_property_rental.csv")
