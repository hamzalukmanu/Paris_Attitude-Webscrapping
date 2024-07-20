import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Initialize WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Comment out or remove this line to disable headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Helper function for safe text extraction
def safe_extract_text(element, class_name):
    try:
        # Extract text from element based on class name
        text = element.find(class_=class_name).get_text(strip=True)
        return text if text else 'N/A'  # Return 'N/A' if the text is empty
    except AttributeError:
        return 'N/A'  # Return 'N/A' if the element is not found

# Function to scrape property data
def scrape_property_data(driver, url):
    try:
        # Open the website
        driver.get(url)

        # Wait for the property list to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'card'))
        )

        # Scroll to the bottom of the page to load all properties (if infinite scrolling is implemented)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(20)  # Wait for content to load

        # Get the page source and parse with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Debugging: Print the page source or a sample of it
        # print("Page Source:")
        # print(soup.prettify())

        # Extract property details
        property_details = []
        for property_card in soup.find_all(class_='card'):
            try:
                # Debugging: Print the HTML of the property card
                print("Property Card HTML:")
                print(property_card.prettify())
                
                name = safe_extract_text(property_card, 'cardName')
                address = safe_extract_text(property_card, 'cardAddress')
                price = safe_extract_text(property_card, 'cardPrice')
                newPrice = safe_extract_text(property_card, 'cardNewPrice')
                availability = safe_extract_text(property_card, 'cardAvailability')
                occupants = safe_extract_text(property_card, 'cardOccupants')
                floor = safe_extract_text(property_card, 'cardFloor')
                arrondissement = safe_extract_text(property_card, 'cardArrondissement')
                energy = safe_extract_text(property_card, 'cardEnergy')
                ghg = safe_extract_text(property_card, 'cardGHG')

                property_details.append({
                    'name': name,
                    'address': address,
                    'price': price,
                    'newPrice': newPrice,
                    'availability': availability,
                    'occupants': occupants,
                    'floor': floor,
                    'arrondissement': arrondissement,
                    'energy': energy,
                    'ghg': ghg,
                })
            except Exception as e:
                print(f"Error processing property: {e}")
                continue

        return property_details

    except Exception as e:
        print(f"Error occurred: {e}")
        return []

# URL of the e-commerce site category page (example)
url = 'https://www.parisattitude.com/rent-apartment/furnished-rental/index,rentals.aspx?p=69'

# Scrape the data
property_details = scrape_property_data(driver, url)

# Close the WebDriver
driver.quit()

# Save data to CSV
df = pd.DataFrame(property_details)
df.to_csv('property_details.csv', index=False)

print(df)
print("Data scraping completed and saved to property_details.csv")
