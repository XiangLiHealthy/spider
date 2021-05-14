import requests
import chardet
import time
import  urllib3
import  ssl

tmp = urllib3.disable_warnings()

URL_HTTPS = 'https://127.0.0.1:9999'
ssl._create_default_https_context = ssl._create_stdlib_context
s = requests.Session()

def test_post(url, data):
    try:
        r = requests.post(url, data)
        if r.status_code == 200 :
            r.encoding = chardet.detect(r.content)["encoding"]
            return r.text
    except Exception as e :
        print ('tets_post url:{}, error:{}'.format(url, e))
    return None

def https_get(url, data):
    try:
        print ('https_get url:{}'.format(url))

        r = s.get(url, verify=False)
        if r.status_code == 200:
            r.encoding = chardet.detect(r.content)["encoding"]
            return r.text
    except Exception as e :
        print (e)

    return None

def test_https_post(url, data):

    return

if __name__ == '__main__':
    while True :
        # data = {'user' : 'hellow'}
        # r = test_post("http://127.0.0.1:9999/test_post", data)
        # print (r)

        last = time.perf_counter()
        print (https_get(URL_HTTPS + '/', ''))
        print ('use time:{}'.format(time.perf_counter() - last))

        #time.sleep(0.1)

