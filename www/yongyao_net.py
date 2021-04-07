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

path = '~'

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
    def login(self):
        log_url = 'https://auth.dxy.cn/accounts/login?logoDqId=21523&method=2&qr=false&service=https%3a%2f%2fdxy.com%2fauth%2flogin%2fdxy%3fredirect_uri%3daHR0cHM6Ly9keHkuY29tLw=='
        self.browser.get(log_url)
        log_title = self.browser.find_element_by_xpath("//h3[@class = 'login__head_log J-login-method']")
        log_title.click()

        username = self.browser.find_element_by_name('username')
        password = self.browser.find_element_by_name('password')
        submit = self.browser.find_element_by_xpath("//button[@type='submit']")

        username.send_keys('13883372441')
        password.send_keys('Xl2016xl')
        submit.click()
        sleep(10)

        return

    def reconnet_chrome(self):
        self.browser.close()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(5)

    def get_items(self):
        try:
            #get main page
            self.browser.get("https://dxy.com/firstaids")

            #get aid_card
            soup = BeautifulSoup(self.browser.page_source)
            aid_cards = soup.find_all('div', attrs = {'class' : 'first-aid-card'})

            first_aids = []
            for card in aid_cards :
                main_category = card.find('div', attrs = {'class' : 'header-title'})
                body_items = card.find_all('div', attrs = {'class' : 'body-item'})
                for body_item in body_items :
                    child_category = body_item.find('div', attrs = {'class' : 'common-tag-content'})
                    name_items = body_item.find_all('div', attrs = {'class' : 'link-line'})
                    for name in name_items :
                        first_aid = {}
                        first_aid['name'] = name.get_text()
                        first_aid['url'] = name.contents[0].attrs['href']
                        first_aid['main_category'] = main_category.get_text()
                        first_aid['child_category'] = child_category.get_text()
                        first_aids.append(first_aid)

            #get head1, head2, items
            return first_aids
        except Exception as e :
            print (e)

        return None

    def get_content(self, name, url):
        try:
            #opend web
            self.browser.get(url)
            soup = BeautifulSoup(self.browser.page_source)

            text = ''
            middle = soup.find('div', attrs = {'class' : 'article-detail-content'})
            text = middle.find('h1').get_text() + '\n'
            paragrahs = middle.find_all('div', attrs = {'class' : 'html-parse continuous-img-no-margin article-html'})
            index = 0
            for div in paragrahs :
                tags = div.find_all(['p', 'span', 'img', 'video'])
                for tag in tags :
                    if 'img' == tag.name or 'video' == tag.name :
                        url = tag.attrs['src']
                        pos = url.rfind('.')
                        prefix = url[pos:]
                        file = path + '/jijiu/{}-{}{}'.format(name, index, prefix)
                        index += 1
                        downloader.get_img(url, file)
                        text += '\n如图：{}\n'.format(file)
                    text += tag.get_text()

            return text
        except Exception as e :
            print (e)
            return ''

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

            # get all button in per page

            drug_buttons = []
            while (True) :
                drug_button = self.browser.find_elements_by_xpath("//div[class = 'mainbody']/div[1]/div[0]/div[1]/div[0]/div[1]/span[@id = 'Labelypmc']/div[@id]")
                drug_button = self.browser.find_elements_by_xpath("//span[@id = 'Labelypmc']/div[@id]")
                drug_buttons += drug_button
                if len(drug_button) < 14 :
                    break
                #page_title = self.browser.find_elements_by_xpath("//span[@id = 'Labelypmc']/div[0]/span")

                page_num = self.browser.find_elements_by_xpath("//div[@class = 'jlhspagenum']")
                for num in page_num:
                    if '下一页' == num.text :
                        if hasattr(num, 'href'):
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
                contents['degree'] += degree.text + '\n'

            # get detail
            details = self.browser.find_elements_by_xpath("//div[@class = 'ypdjzsnr']")
            for detail in details :
                contents['detail'] += detail.text + '\n'

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
                    contents['classify'] = catogory

                    self.save(contents)
        finally:
            self.browser.close()

        return

if __name__ == '__main__' :
    tool = SpiderDisesea()
    urls = tool.perform()
    print (urls)