from config import (
    get_chrome_web_driver,
    get_web_driver_options,
    set_browser_as_incognito,
    set_ignore_certificate_error,
    disable_popup,
    BASE_URL,
    SEARCH,
    EMAIL,
    PASSWORD,
    DIRECTORY
)
import time
from datetime import datetime
import json
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GenerateReport:
    def __init__(self, file_name, base_link, data):
        self.file_name = file_name
        self.base_link = base_link,
        self.data = data
        report ={
            'title':self.file_name,
            'date':self.get_date(),
            'total':len(self.data),
            'best_book':self.get_best_book(),
            'base_link':self.base_link,
            'data':self.data,
        }
        with open(f'{DIRECTORY}/{self.file_name}.json', 'w') as f:
            json.dump(report, f)
        print('Done...')

    def get_best_book(self):
        try:
            return sorted(self.data, key= lambda k: k['rating'])[-1]
        except Exception as e:
            print(e)
            print('Proplem with sorting books')
            return None

    def get_date(self):
        now = datetime.now()
        return now.strftime("%d/%m/%y %H:%M:%S")



class GoodreadsAPI:
    def __init__(self, email, password, search_term, base_url):
        self.search_term = search_term
        self.base_url = base_url
        self.email = email
        self.password = password
        options = get_web_driver_options()
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        disable_popup(options)
        self.driver = get_chrome_web_driver(options)
  

    def run(self):
        self.driver.get(self.base_url)
        time.sleep(5)
        self.login(self.email, self.password)
        links = self.search_for(self.search_term)
        new_books = self.get_books_info(links)
        time.sleep(4)
        self.driver.quit()
        return new_books

    def get_books_info(self, links):
        new_books = []
        if links:
            n = 1
            for link in links:
                print(f'Book {n} - getting data...')
                book = self.get_book_info(link)
                if book:
                    new_books.append(book)
                    print('Success')
                else:
                    print(None)
                n+=1
            return new_books
        else:
            print('No Books Found...')
            return new_books

    def get_book_info(self, link):
        self.driver.get(link)
        time.sleep(3)
        title = self.get_title()
        author = self.get_author()
        description = self.get_description()
        rating = self.get_rating()
        paperback = self.get_paperback()
        published = self.get_published()
        if  title and author and description and rating and paperback and published:
            book = {
                'title':title,
                'author':author,
                'description':description,
                'rating':rating,
                'paperback':paperback,
                'published':published,
                'link':link
            }
            return book
        else :
            return None
        
        

    def get_published(self):
        try:
            date = self.driver.find_element_by_xpath('//*[@id="details"]/div[2]').text
            date = date[date.find('Published')+9:date.find('by')]
            return date
        except (NoSuchElementException, Exception) :
            return None

    def get_paperback(self):
        try:
            try:
                pages = self.driver.find_element_by_xpath('//*[@id="details"]/div[1]/span[2]').text
            except NoSuchElementException:
                return self.driver.find_element_by_xpath('//*[@id="details"]/div[1]/span').text
            pages = pages[:pages.find('p')]
            try:
                return int(pages)
            except Exception as e:
                pages = self.driver.find_element_by_xpath('//*[@id="details"]/div[1]/span[3]').text
                pages = pages[:pages.find('p')]
                return int(pages)
        except (NoSuchElementException, Exception):
            return None

    def get_rating(self):
        try:
            rating = self.driver.find_element_by_xpath('//*[@id="bookMeta"]/span[2]').text 
            return float(rating)
        except (NoSuchElementException, Exception):
            return None

    def get_description(self):
        try:
            try:
                element = self.driver.find_element_by_xpath('//*[@id="description"]/a')
            except NoSuchElementException:
                return self.driver.find_element_by_xpath('//*[@id="description"]/span[1]').text.decode('unicode_escape')
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.click(element)
            actions.perform()
            element1 =  self.driver.find_element_by_id('description').text
            return element1[:element1.find('(less)')].decode('unicode_escape')
        except Exception:
            return None

    def get_author(self):
        try:
            return self.driver.find_element_by_xpath('//*[@id="bookAuthors"]/span[2]/div/a/span').text
        except NoSuchElementException:
            return None

    def get_title(self):
        try:
            return self.driver.find_element_by_id('bookTitle').text.replace('\n','')
        except NoSuchElementException:
            return None

    def login(self, email, password):
        email_input = self.driver.find_element_by_id('userSignInFormEmail')
        password_input = self.driver.find_element_by_id('user_password')
        btn = self.driver.find_element_by_class_name('gr-button')
        email_input.send_keys(email)
        password_input.send_keys(password)
        btn.send_keys(Keys.ENTER)
        time.sleep(7)
        
    def search_for(self,search_term):
        b_btn = self.driver.find_element_by_xpath('/html/body/div[2]/div/header/div[3]/div/nav/ul/li[3]')
        actions = ActionChains(self.driver)
        actions.move_to_element(b_btn)
        actions.click(b_btn)
        actions.perform()
        time.sleep(3)
        ge_btn = self.driver.find_element_by_xpath('/html/body/div[2]/div/header/div[3]/div/nav/ul/li[3]/div/div/div/div/div/span/div/div/ul/li[4]')
        actions = ActionChains(self.driver)
        actions.move_to_element(ge_btn)
        actions.click(ge_btn)
        actions.perform()
        time.sleep(3)
        search_input = self.driver.find_element_by_id('shelf')
        search_input.send_keys(self.search_term)
        search_input.send_keys(Keys.ENTER) 
        time.sleep(9)
        box = self.driver.find_elements_by_class_name('coverBigBox')
        box2 = self.driver.find_elements_by_class_name('bigBoxBody')
        title = box[0].find_element_by_class_name('brownBackground').text
        links =[]
        try:
            results = box2[0].find_elements_by_tag_name(
                "a"
            )
            for link in results :
                if link.get_attribute('class') != 'actionLink':
                    links.append(link.get_attribute('href'))
            print(f"{title} {len(links)} links")
            return(links)
        except Exception as e:
            print("Didn't get any books...")
            print(e)
            return(links)
        

if __name__ == '__main__':
    print('Script starts...')
    goodreads = GoodreadsAPI(EMAIL, PASSWORD, SEARCH, BASE_URL)
    data = goodreads.run()
    GenerateReport(SEARCH, BASE_URL, data)
    

    