from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import re
import time
import sys
import requests
from bs4 import BeautifulSoup


class AmazonBookParser:
    def __init__(self, url, num_pages):
        self.num_pages = num_pages
        self.pages = [Page(url, page) for page in range(1, num_pages + 1)]

    def get_cheap_books(self, price_):
        with ThreadPoolExecutor(max_workers=self.num_pages, thread_name_prefix="Thread") as exe:
            jobs = [exe.submit(page.get_all_books) for page in self.pages]
            for job in as_completed(jobs):
                for book in job.result():
                    if book["price"] <= price_:
                        self.print_a_book(book)

    def print_a_book(self, book):
        print(f'{book["title"]} -- ${book["price"]} from page {book["page"]}')


class Page:
    def __init__(self, url, page_num):
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.page_num = page_num

    def get_all_books(self):
        books = []
        books_soup = self.parse_page()
        for book in books_soup:
            books.append(self.parse_book(book))
        print(f"====got all books of page {self.page_num} from: {threading.current_thread().name}")
        return books

    def parse_book(self, book_soup):
        title = book_soup.find("span").get_text()
        price = book_soup.find("span", class_=re.compile("p13n-sc-price")).get_text()
        return {"title": title, "price": float(price[1:]), "page": self.page_num}

    def parse_page(self):
        thread = threading.current_thread().name
        print(f"====start loading page {self.page_num} from: {thread}")
        html = requests.get(self.url, headers=self.headers, params={"pg": self.page_num}).text
        print(f"====page {self.page_num} loaded from: {thread}")
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all("div", class_="zg-grid-general-faceout")


if __name__ == "__main__":

    URL = "https://www.amazon.com/gp/new-releases/books"
    NUM_PAGES = 5

    # price_to_compare = 15.0

    try:
        price_to_compare = float(sys.argv[1])
    except IndexError:
        print("Please set price")
        sys.exit(0)
    except ValueError:
        print("Pass price as a number")
        sys.exit(0)

    start = time.perf_counter()

    p = AmazonBookParser(url=URL, num_pages=NUM_PAGES)
    p.get_cheap_books(price_to_compare)

    elapsed = time.perf_counter() - start
    print(elapsed)
