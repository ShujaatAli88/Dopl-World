import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urljoin

class MySpider(scrapy.Spider):
    name = 'dopl'
    start_urls = ['https://doplworld.com/']

    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response):
        self.driver.get(response.url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gallery_card")))
        time.sleep(2)  # Wait for the page to fully render
        body = self.driver.page_source
        
        all_products = scrapy.Selector(text=body).css("a.gallery_card.has_caption::attr(href)").getall()
        for product in all_products:
            orig_url = urljoin(response.url, product)
            yield scrapy.Request(orig_url, callback=self.product_details, meta={
                "Product Link" : orig_url
            })
            
    def product_details(self, response):
        self.driver.get(response.url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "page_content")))
        time.sleep(2)
        content = self.driver.page_source
        
        image_link = scrapy.Selector(text=content).css("body > div.main_container > div.content_container > div:nth-child(1) > div > div > div.page.container.container_width > bodycopy > div > img:nth-child(2)::attr(src)").get()
        product_desc = scrapy.Selector(text=content).css("div.page_content.clearfix::text").getall()
        product_desc = " ".join([desc.strip() for desc in product_desc if desc.strip()])
        price = scrapy.Selector(text=content).css("div.page_content.clearfix>div>div>div>b::text").get()
        new_price = ""
        if price is None:
            new_price = scrapy.Selector(text=content).css("div.page_content.clearfix>div>div>div>b>div>b::text").get()
        product = scrapy.Selector(text=content).css("div.page_content.clearfix > div>div>b::text").get()
        
        product_Name = ""
        product_Color = ""
        
        if('•' in product):
            product_list = product.split('•')
            product_Name = product_list[0].strip()
            product_Color = product_list[1].strip
        
        elif(',' in product):
            product_list = product.split(',')
            product_Name = product_list[0].strip()
            product_Color = product_list[1].strip()
        
        else:
            product_Name = product
            product_Color = "Not Given"
        yield {
            "Product Link": response.meta.get("Product Link"),
            "Product Title" : product_Name,
            "Product Color" : product_Color,
            "Image Link": urljoin(response.url, image_link),
            "Product Description": product_desc.strip() if product_desc else None,
            "Product Price": price.strip() if price else new_price.strip()
        }


    def closed(self, reason):
        self.driver.quit()
        
        

