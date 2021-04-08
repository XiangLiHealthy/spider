import downloader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import bs4

from bs4 import BeautifulSoup
from time import sleep
import data_store
import downloader

path = '/home/xiangbaosong/work'

class SpiderDisesea:
    def __init__(self):
        options = webdriver.ChromeOptions()
        #add_argument('--headless')
        #self.browser = webdriver.Chrome(options=options)

        # 禁止图片和css加载
        prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
        options.add_experimental_option("prefs", prefs)

        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(5)

    def reconnet_chrome(self):
        self.browser.close()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(5)

    def save(self, contents):
        try:
            headers = ['名称', '种类', '安全等级', '详细内容']
            file = path + '/妊娠期糖尿病药物信息.csv'

            datas = [contents['drug'], contents['classify'], contents['degree'], contents['detail']]

            data_store.write_content(file, headers, datas)
        except Exception as e :
            print (e)

        return

    def get_all_catory(self):
        try:
            url = "http://www.yongyao.net/new/yhyyfjcxb.aspx"
            self.browser.get(url)

            #get options lables
            catorys = []
            options = self.browser.find_elements_by_xpath("//select/option")
            for option in options :
                if '请选择类别' == option.text :
                    continue

                catorys.append(option)
        except Exception as e :
            print('get all catogry error:{}'.format(e))

        return catorys

    def get_all_drug_button(self, catogory):
        try:
            catogory.click()

            # click button
            catogory_select = self.browser.find_element_by_xpath("//div[@class = 'jlhstitlepagebtn']")
            catogory_select.click()
            sleep(0.1)

            # get all button in per page

            drug_buttons = []
            while (True) :
                drug_button = self.browser.find_elements_by_xpath("//span[@id = 'Labelypmc']/div[@id]")
                drug_buttons += drug_button

                soup = BeautifulSoup(self.browser.page_source, 'html.parser')
                num_title = soup.find('span', attrs = {'id' : 'Labelypmc'})
                nums = num_title.find_all('span')
                current = nums[0].get_text()
                total = nums[1].get_text()
                if (current == total) :
                    break

                sleep(1)
                page_num = self.browser.find_elements_by_xpath("//div[@class = 'jlhspagenum']")
                for num in page_num:
                    if '下一页' == num.text :
                        num.click()
                        continue

                break

        except Exception as e:
            print ('get_all_drug_button error:{}'.format(e))

        return drug_buttons

    def get_content(self, drug_button):
        try:
            # click drug button
            drug_button.click()

            # submit select
            select_button = self.browser.find_element_by_xpath("//div[@class = 'jlhstitlepagebtn1']")
            select_button.click()

            contents = {}
            contents['degree'] = ''
            contents['detail'] = ''

            # get degree
            degrees = self.browser.find_elements_by_xpath("//div[@class = 'ypdjzs']")
            for degree in degrees :
                contents['degree'] += degree.text + '\n\n'

            # get detail
            details = self.browser.find_elements_by_xpath("//div[@class = 'ypdjzsnr']")
            for detail in details :
                contents['detail'] += detail.text + '\n\n'

        except Exception as e :
            print ('get content error:{}'.format(e))

        return contents

    def perform(self) :
        try:
            #self.login()

            # 获取所有药物种类
            catorys = self.get_all_catory()

            # 获取所有种类下的药品名称
            for catogory in catorys :
                drug_buttons = self.get_all_drug_button(catogory)

                # 选择每个药物，并解析内容
                for drug_button in drug_buttons :
                    contents = self.get_content(drug_button)
                    contents['drug'] = drug_button.text
                    contents['classify'] = catogory.text

                    self.save(contents)
                    sleep(0.1)
        finally:
            self.browser.close()

        return

if __name__ == '__main__' :
    tool = SpiderDisesea()
    urls = tool.perform()
    print (urls)