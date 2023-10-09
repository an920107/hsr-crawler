from interface.disposable import Disposable
from util.chrome import Chrome
from util.exceptions import CaptchaException, SoldOutException
from util.settings import settings
from model.request import SearchRequest, BookRequest
from model.discount import Discount
from model.train import Train

from datetime import time
from ddddocr import DdddOcr
from pyimgur import Imgur
from undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import os


class HSR(Disposable):

    def __init__(self, dispose_sec: float | None = None) -> None:
        # Disposable 初始化
        super().__init__(dispose_sec=dispose_sec)
        self.train_list = []

        # Imgur 初始化
        self.__imgur = Imgur(settings.imgur_client_id,
                             settings.imgur_client_secret)

        # Selenium 初始化
        URL = "https://irs.thsrc.com.tw/IMINT/"

        options = ChromeOptions()
        options.add_argument("--disable-notifications")
        self.__chrome = Chrome(options=options)
        self.__chrome.get(URL)

        # 同意 cookie
        try:
            self.__chrome.find_element_and_wait(
                By.XPATH, "//*[@id='cookieAccpetBtn']", 1000).click()
        except:
            pass

    # Implement [Disposable]
    def dispose(self) -> None:
        self.__chrome.quit()
        try:
            os.remove(f"tmp/captcha/{self.uuid}.png")
            os.remove(f"tmp/result/{self.uuid}.png")
        except:
            pass

    # 取得時刻表
    def get_time_table(self, search_req: SearchRequest) -> list[Train]:

        # 將時間改成 30 分鐘為一單位
        search_req.departure = search_req.departure.replace(
            minute=search_req.departure.minute // 30 * 30)

        # 因為驗證碼有可能偵測錯誤，若偵測錯誤則重試
        MAX_TRY = 5
        for _ in range(MAX_TRY):
            try:
                # 輸入訂票資訊
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[3]/div[1]/div/div[1]/div/select"
                )).select_by_visible_text(search_req.station_from)
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[3]/div[1]/div/div[2]/div/select"
                )).select_by_visible_text(search_req.station_to)
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[4]/div[1]/div[1]/div/select"
                )).select_by_visible_text(str(search_req.adult_count))
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[4]/div[1]/div[2]/div/select"
                )).select_by_visible_text(str(search_req.child_count))
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[4]/div[1]/div[3]/div/select"
                )).select_by_visible_text(str(search_req.heart_count))
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[4]/div[1]/div[4]/div/select"
                )).select_by_visible_text(str(search_req.elder_count))
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[4]/div[1]/div[5]/div/select"
                )).select_by_visible_text(str(search_req.student_count))
                self.__chrome.execute_script(
                    f"document.getElementById('toTimeInputField').\
                    setAttribute('value', '{search_req.departure.strftime('%Y/%m/%d')}')")
                Select(self.__chrome.find_element(
                    By.XPATH,
                    "//*[@id='BookingS1Form']/div[3]/div[2]/div/div[2]/div[1]/select"
                )).select_by_visible_text(search_req.departure.strftime("%H:%M"))

                # 驗證碼
                self.__chrome.find_element(
                    By.ID, "BookingS1Form_homeCaptcha_passCode").screenshot(f"tmp/captcha/{self.uuid}.png")
                with open(f"tmp/captcha/{self.uuid}.png", "rb") as image_file:
                    image_bytes = image_file.read()
                security_code = DdddOcr(
                    show_ad=False).classification(image_bytes)
                security_code_blank = self.__chrome.find_element(
                    By.ID, "securityCode")
                security_code_blank.clear()
                security_code_blank.send_keys(security_code)

                self.__chrome.find_element(By.ID, "SubmitButton").click()

                error_elm = self.__chrome.find_element(By.ID, "divErrMSG")
                # error div is not hidden
                if (len(error_elm.get_attribute("style")) == 0):
                    error_msg = self.__chrome.find_element(
                        By.XPATH, "//*[@id='feedMSG']/span/ul/li/span").text
                    if "售完" in error_msg:
                        raise SoldOutException()
                    else:
                        raise CaptchaException()

                break

            except CaptchaException:
                continue

            except SoldOutException:
                return []

        # 取得班次
        self.train_list = list(map(lambda e: Train(departure=e[0], arrival=e[1], no=e[2], discounts=e[3]), zip(
            # e.text: string of time -> 00:00
            map(lambda e: time(hour=int(e.text[:2]), minute=int(e.text[3:])),
                self.__chrome.find_elements(By.ID, "QueryDeparture")),
            # e.text: string of time -> 00:00
            map(lambda e: time(hour=int(e.text[:2]), minute=int(e.text[3:])),
                self.__chrome.find_elements(By.ID, "QueryArrival")),
            # e.text: string of train No.
            map(lambda e: int(e.text),
                self.__chrome.find_elements(By.ID, "QueryCode")),
            # e.text: string of discounts splitted by "\n"
            map(lambda e: list(map(lambda s: Discount(s), e.text.split("\n"))),
                self.__chrome.find_elements(By.CSS_SELECTOR, "div[class='discount uk-flex']")))))

        return self.train_list

        # ---DEBUG---
        # for i in range(len(train_list)):
        #     train = train_list[i]
        #     print(
        #         f"{i + 1:2d} {train.no:4d} {train.departure} {train.arrival} {train.discounts}")
        # -----------

    # 訂票
    def book_ticket(self, book_req: BookRequest) -> str:
        # 選擇班次
        self.__chrome.find_elements(By.CSS_SELECTOR, "input[type='radio']")[
            book_req.selected_index].click()
        self.__chrome.find_element(
            By.XPATH, "//*[@id='BookingS2Form']/section[2]/div/div/input").click()

        # 輸入身份資訊
        id_blank = self.__chrome.find_element(By.ID, "idNumber")
        id_blank.clear()
        id_blank.send_keys(book_req.id_card_number)
        phone_blank = self.__chrome.find_element(By.ID, "mobilePhone")
        phone_blank.clear()
        phone_blank.send_keys(book_req.phone)
        email_blank = self.__chrome.find_element(By.ID, "email")
        email_blank.clear()
        email_blank.send_keys(book_req.email)
        self.__chrome.find_element(
            By.XPATH, "//*[@id='BookingS3FormSP']/section[2]/div[3]/div[1]/label/input").click()

        # 完成訂票
        self.__chrome.find_element(By.ID, "isSubmit").click()

        # 關閉學生優惠提醒視窗
        try:
            self.__chrome.find_element_and_wait(
                By.ID, "step4StudentModalBtn", 800).click()
        except:
            pass

        # 截圖並上傳到 Imgur
        self.__chrome.find_element(
            By.XPATH, "//*[@id='BookingS4Form']/section[1]").screenshot(f"tmp/result/{self.uuid}.png")
        img = self.__imgur.upload_image(f"tmp/result/{self.uuid}.png")

        return img.link_huge_thumbnail
