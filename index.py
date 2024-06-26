import json
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time
import random
import psutil
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote

def kill_chrome():
    PROCNAME = "chrome"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--incognito")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-images")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def check_is_phone(data_item_id):
    patterns = [
        r"\+84\d{9,10}",  # Matches '+84' followed by 9 or 10 digits
        r"01[0-9]\d{8,9}",  # Matches '01x' followed by 8 or 9 digits
        r"02[0-9]\d{8,9}",  # Matches '02x' followed by 8 or 9 digits
        r"03[0-9]\d{8,9}",  # Matches '03x' followed by 8 or 9 digits
        r"04[0-9]\d{8,9}",  # Matches '04x' followed by 8 or 9 digits
        r"05[0-9]\d{8,9}",  # Matches '05x' followed by 8 or 9 digits
        r"06[0-9]\d{8,9}",  # Matches '06x' followed by 8 or 9 digits
        r"07[0-9]\d{8,9}",  # Matches '07x' followed by 8 or 9 digits
        r"08[0-9]\d{8,9}",  # Matches '08x' followed by 8 or 9 digits
        r"09[0-9]\d{8,9}",  # Matches '09x' followed by 8 or 9 digits
    ]
    for pattern in patterns:
        if re.search(pattern, data_item_id):
            return True
    return False

def get_tax_code(url):
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]
    headers = {
        "User-Agent": random.choice(headers_list),
    }
    res = requests.get(url, headers=headers)
    tax_code = ''
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        table_info = soup.find("table", class_="table-taxinfo")
        tax_code = table_info.find("td", itemprop="taxID").text
    return tax_code

def check_tax_code_masothue(name):
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]
    headers = {
        "User-Agent": random.choice(headers_list),
    }
    search_query = quote(name.lower())
    url = f"https://masothue.com/Search/?q={search_query}&type=auto&token=grPD2qjMpS&force-search=1"
    res = requests.get(url, headers=headers)
    tax_code = ''
    print(res.url)
    if '?q=' not in res.url:
        tax_code = get_tax_code(res.url)
        print(tax_code)
    else:
        soup = BeautifulSoup(res.text, "html.parser")
        table_info = soup.find(class_="tax-listing")
        div_tags = table_info.find("div", {"data-prefetch": True})
        if div_tags:
            prefetch_value = div_tags.get('data-prefetch')
        url = f"https://masothue.com{prefetch_value}"
        tax_code = get_tax_code(url)
        print(tax_code)
    return tax_code
    
def get_info_google_map(name, address, tax_code):
    driver = setup_driver()
    try:
        driver.get("https://www.google.com/maps")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        query = f"{name}, {address}"
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.url_contains("/maps/")
        )
        search_result_url = driver.current_url
        array_images = []
        address = ''
        website = ''
        phone = ''
        print(query)
        time.sleep(1)  # Chờ một chút để trang web tải đầy đủ
        
        if "place/" in search_result_url:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "lMbq3e"))
            )
            element_title = driver.find_element(By.CLASS_NAME, "lMbq3e")
            title = element_title.find_element(By.CLASS_NAME, "DUwDvf")
            tax_code_map = check_tax_code_masothue(title.text)
            print(f'current tax code: {tax_code}')
            if tax_code_map in tax_code:
                info_locations = driver.find_elements(By.CLASS_NAME, "CsEnBe")
                for element in info_locations:
                    data_item_id = element.get_attribute("data-item-id")
                    if data_item_id == "address":
                        address = element.find_element(By.CLASS_NAME, "rogA2c").text
                        print(f"Address: {address}")
                    elif data_item_id == "authority":
                        website = element.find_element(By.CLASS_NAME, "rogA2c").text
                        print(f"Website: {website}")
                    elif check_is_phone(data_item_id):
                        phone = element.find_element(By.CLASS_NAME, "rogA2c").text
                        print(f"Phone: {phone}")
                
                click_to_images = driver.find_elements(By.CLASS_NAME, "YNB9Sd")
                if click_to_images:
                    for click_to_image in click_to_images:
                        try:
                            WebDriverWait(click_to_image, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".Dx2nRe")))
                            button_click = click_to_image.find_element(By.CLASS_NAME, "Dx2nRe")
                            total_images = 10
                            count_images = click_to_image.find_element(By.CLASS_NAME, "YkuOqf")
                            count_images_text = count_images.get_attribute("textContent")
                            count_images = int(re.search(r"\d+", count_images_text).group())
                            if count_images > 1:
                                total_images = min(10, count_images)
                                button_click.click()
                                try:
                                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "id-play")))
                                except TimeoutException:
                                    print("No company found")
                                
                                buttons = driver.find_elements(By.CLASS_NAME, "id-play")
                                for button in buttons:
                                    for _ in range(total_images):
                                        get_next = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "eU5Rrb")))
                                        get_next.click()
                                        elements = driver.find_elements(By.CLASS_NAME, "selected")
                                        for row in elements:
                                            element_images = row.find_elements(By.CLASS_NAME, "U39Pmb")
                                            for img in element_images:
                                                background_image = img.value_of_css_property("background-image")
                                                match = re.search(r'url\("(.+?)"\)', background_image)
                                                if match:
                                                    array_images.append(match.group(1))
                                break 
                            else:
                                button_click.click()
                                elements = driver.find_elements(By.CLASS_NAME, "selected")
                                for row in elements:
                                    element_images = row.find_elements(By.CLASS_NAME, "U39Pmb")
                                    for img in element_images:
                                        background_image = img.value_of_css_property("background-image")
                                        match = re.search(r'url\("(.+?)"\)', background_image)
                                        if match:
                                            array_images.append(match.group(1))
                                break
                        except TimeoutException:
                            print("No Images")
            else:
                print("Incorrect tax code")
        else:
            print("Không tìm thấy công ty")
            return None
    
    finally:
        driver.close()
        driver.quit()
        kill_chrome()
    
    data = {
        "images": array_images,
        "website": website,
        "address": address,
        "phone": phone,
    }
    
    return data
        
def get_profile_company(url, slug_location, headers_list):
    headers = {
        "User-Agent": random.choice(headers_list),
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            table_info = soup.find("table", class_="table-taxinfo")
            name = table_info.find("th", itemprop="name")
            address = table_info.find("td", itemprop="address")
            representative = table_info.find("span", itemprop="name")
            phone = table_info.find("td", itemprop="telephone")
            tax_code = table_info.find("td", itemprop="taxID").text
            table_business = soup.find("table", class_="table")
            company_name = name.text if name else ""
            company_address = address.text if address else ""
            company_phone = phone.text if phone else ""
            comapny_representative = representative.text if representative else ""
            company_business = []
            if table_business:
                for td in table_business.select("tr > td:nth-child(1)"):
                    company_business.append(td.text)
            data_google_map = get_info_google_map(company_name, company_address, tax_code)
            if data_google_map:
                if data_google_map is None:
                    data_google_map = {
                        "address": "",
                        "website": "",
                        "phone": "",
                        "images": [],
                    }
                data = {
                    "name": company_name,
                    "address": company_address,
                    "phone": company_phone,
                    "representative": comapny_representative,
                    "business": company_business,
                    "location": slug_location,
                    "tax_code": tax_code,
                    "address_map": data_google_map["address"],
                    "website": data_google_map["website"],
                    "phone_map": data_google_map["phone"],
                    "images": data_google_map["images"],
                }
                post_to_php(data, "companies")
                return data
            else:
                return None
        else:
            print(f"Failed to retrieve company profile from {url}. Status code: {res.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching company profile from {url}: {str(e)}")
        return None

def get_data_location(url, slug_location, headers_list):
    base_url = "https://masothue.com/"
    page_number = 1
    companies_info = []
    while True:
        headers = {
            "User-Agent": random.choice(headers_list),
        }
        current_url = f"{url}?page={page_number}" if page_number > 1 else url
        try:
            res = requests.get(current_url, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                current_page = soup.find(class_="current")
                name_company = soup.find(class_="tax-listing")
                if not name_company:
                    print(f"No company listings found on page {page_number}. Stopping.")
                    break
                div_tags = name_company.find_all("div", {"data-prefetch": True})
                for div_tag in div_tags:
                    data_prefetch_value = div_tag["data-prefetch"]
                    company_url = urllib.parse.urljoin(base_url, data_prefetch_value)
                    company_info = get_profile_company(company_url, slug_location, headers_list)
                    if company_info:
                        companies_info.append(company_info)
                if page_number > 1 and current_page.text.strip() == "1":
                    print(f"Reached the first page again at page number {page_number}. Stopping.")
                    break
                else:
                    page_number += 1
            else:
                print(f"Failed to retrieve page {page_number}. Status code: {res.status_code}")
                break
        except Exception as e:
            print(
                f"Exception occurred while fetching data from {current_url}: {str(e)}"
            )
            break
    return companies_info

def post_to_php(data, type=None):
    url = "https://go.coinspyx.com/tool/masothue/pust_data.php"
    # url = "http://localhost/Intern/masothue/"
    json_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    print(data)
    params = {"type": type}
    response = requests.post(url, data=json_data, params=params)
    if response.status_code == 200:
        print(response.text)
    else:
        print(
            f"Failed to send data to the endpoint. Status code: {response.status_code}"
        )

def get_communes(district, slug_district, headers_list):  # xã
    headers = {
        "User-Agent": random.choice(headers_list),
    }
    commune_url = district
    res = requests.get(commune_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    if res.status_code == 200:
        commune_data = soup.find_all(class_="cat-item col-xs-6 col-md-12")
        communes = []
        if commune_data:
            for item in commune_data:
                relative_link = item.find("a")["href"]
                location_link = urllib.parse.urljoin(commune_url, relative_link)
                location_name = item.text.strip()
                print(location_name)
                slug = relative_link.split("/")[-1]
                communes.append(
                    {
                        "name": location_name,
                        "url": location_link,
                        "parent_id": slug_district,
                        "slug": slug,
                        "type": "location",
                    }
                )
            post_to_php(communes, "location")
            for commune in communes:
                get_data_location(commune["url"], commune["slug"], headers_list)
            return communes
        else:
            return []
    else:
        print(res.status_code)

def get_districts(province, slug_city, headers_list):  # huyện
    district_url = province
    headers = {
        "User-Agent": random.choice(headers_list),
    }
    res = requests.get(district_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    if res.status_code == 200:
        district_data = soup.find_all(class_="cat-item col-xs-6 col-md-12")
        districts = []
        for item in district_data:
            relative_link = item.find("a")["href"]
            location_link = urllib.parse.urljoin(district_url, relative_link)
            location_name = item.text.strip()
            print(location_name)
            slug = relative_link.split("/")[-1]
            districts.append(
                {
                    "name": location_name,
                    "url": location_link,
                    "parent_id": slug_city,
                    "slug": slug,
                    "type": "location",
                }
            )
        post_to_php(districts, "location")
        for district in districts:
            time.sleep(1)
            get_data_location(district["url"], district["slug"], headers_list)
            get_communes(district["url"], district["slug"], headers_list)
        return districts
    else:
        print(res.status_code)

def get_location_city(base_url, data, headers_list):  # tinh
    locations = []
    for item in data:
        relative_link = item.find("a")["href"]
        location_link = urllib.parse.urljoin(base_url, relative_link)
        location_name = item.text.strip()
        slug = relative_link.split("/")[-1]
        print(location_name)
        locations.append(
            {
                "name": location_name,
                "url": location_link,
                "slug": slug,
                "parent_id": 0,
                "type": "location",
            }
        )
    post_to_php(locations, "location")
    for location in locations:
        time.sleep(1)
        get_data_location(location["url"], location["slug"], headers_list)
        get_districts(location["url"], location["slug"], headers_list)
    return locations

def main():
    base_url = "https://masothue.com/"
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]
    headers = {
        "User-Agent": random.choice(headers_list),
    }
    res = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    province_data = soup.find_all(class_="cat-item col-xs-6 col-md-12")
    get_location_city(base_url, province_data, headers_list)

def get_business():
    base_url = "https://masothue.com/tra-cuu-ma-so-thue-theo-nganh-nghe"
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    ]
    page_number = 1
    while True:
        headers = {
            "User-Agent": random.choice(headers_list),
        }
        current_url = f"{base_url}?page={page_number}" if page_number > 1 else base_url
        res = requests.get(current_url, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            table_business = soup.find("table", class_="table")
            if table_business:
                rows = table_business.find_all("tr")
                # Kiểm tra xem có dữ liệu hợp lệ trong bảng không
                if (len(rows) > 1):  # Nếu số lượng hàng lớn hơn 1 (số hàng tiêu đề bảng là 1)
                    for row in rows[1:]:  # Bỏ qua hàng đầu tiên vì đó là tiêu đề
                        cells = row.find_all("td")
                        if (
                            len(cells) >= 2
                        ):  # Ensure there are at least two cells in the row
                            code = cells[0].text.strip()
                            name = cells[1].text.strip()
                            data = {
                                "code": code,
                                "name": name,
                            }
                            post_to_php(data, "business")  # Gửi dữ liệu đến endpoint PHP
                    page_number += 1
                else:
                    print(f"Không tìm thấy dữ liệu hợp lệ trong bảng trên trang {current_url}")
                    break
            else:
                print(f"Không tìm thấy bảng dữ liệu trên trang {current_url}")
                break
        else:
            print(f"Lỗi khi truy cập trang {current_url}, mã lỗi {res.status_code}")

if __name__ == "__main__":
    # get_business()
    main()
