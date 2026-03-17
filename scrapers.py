import subprocess
subprocess.run(["playwright", "install", "chromium"], check=True)

from playwright.sync_api import sync_playwright

def get_trendyol_price(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            page.wait_for_timeout(5000)
            price_element = page.query_selector(".discounted")
            image_element = page.query_selector("._carouselImage_abb7111")
            price = None
            image = None
            if price_element:
                price_text = price_element.inner_text().strip()
                price = float(price_text.replace("TL", "").replace(".", "").replace(",", ".").strip())
            if image_element:
                image = image_element.get_attribute("src")
            browser.close()
            return {"price": price, "image": image}
    except Exception as e:
        print(f"Trendyol error: {e}")
    return {"price": None, "image": None}

def get_amazon_price(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(10000)
            price_element = page.query_selector(".a-price-whole")
            image_element = page.query_selector("#landingImage")
            price = None
            image = None
            if price_element:
                price_text = price_element.inner_text().strip()
                price_clean = price_text.replace("\n", "").replace(".", "").replace(",", "").strip()
                price = float(price_clean)
            if image_element:
                image = image_element.get_attribute("src")
            browser.close()
            return {"price": price, "image": image}
    except Exception as e:
        print(f"Amazon error: {e}")
    return {"price": None, "image": None}

def get_price(url):
    if "trendyol.com" in url:
        return get_trendyol_price(url)
    elif "amazon.com.tr" in url:
        return get_amazon_price(url)
    else:
        return {"price": None, "image": None}