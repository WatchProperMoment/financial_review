import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from lxml import etree
import requests
# from longport.openapi import Config, QuoteContext

# def get_index(ctx, index_list):
#     resp = ctx.quote(index_list)
#     index = []
#     for item in resp:
#         v = round((item.last_done - item.prev_close) / item.prev_close * 100, 2)
#         if (v > 0):
#             index.append("<font color='red'>+" + str(v) + "%</font>")
#         else:
#             index.append("<font color='green'>" + str(v) + "%</font>")
#     return index

# def get_china_index(ctx):
#     index = get_index(ctx, ["000001.SH", "399001.SZ", "399006.SZ", "000688.SH"])
#     ret = f'1. 上证指数{index[0]}，深证成指{index[1]}，创业板{index[2]}，科创50{index[3]}，北证50，两市成交亿，较上一日放量亿，家上涨，家下跌，涨跌停:；\n'
#     return ret

# def get_hk_index(ctx):
#     index = get_index(ctx, ["HSI.HK", "HSCEI.HK", "HSTECH.HK"])
#     ret = f'2. 恒生指数{index[0]}，国企指数{index[1]}，恒生科技指数{index[2]}；\n'
#     return ret

# # def get_other_index(ctx):
# #     index = get_index(ctx, ["USDCHN", "HSCEI.HK", "HSTECH.HK"])
# #     ret = f'2. 恒生指数{index[0]}，国企指数{index[1]}，恒生科技指数{index[2]}；'
# #     return ret

# def get_us_index(ctx):
#     resp = ctx.quote([".DJI.US", ".IXIC.US", ".SPX.US"])
#     print(resp)
#     index = []
#     for item in resp:
#         v = round((item.last_done - item.prev_close) / item.prev_close * 100, 2)
#         if (v > 0):
#             index.append("<font color='red'>+" + str(v) + "%</font>")
#         else:
#             index.append("<font color='green'>" + str(v) + "%</font>")
#     ret = f'1. 道琼斯收{index[0]}，纳斯达克收{index[1]}，标普500收{index[2]}；'
#     return ret

# def get_us_china_index(ctx):
#     resp = ctx.quote(["PGJ.US", "YINN.US"])
#     index = []
#     for item in resp:
#         v = round((item.last_done - item.prev_close) / item.prev_close * 100, 2)
#         if (v > 0):
#             index.append("<font color='red'>+" + str(v) + "%</font>")
#         else:
#             index.append("<font color='green'>" + str(v) + "%</font>")
#         v = round((item.post_market_quote.last_done - item.post_market_quote.prev_close) / item.post_market_quote.prev_close * 100, 2)
#         if (v > 0):
#             index.append("<font color='red'>+" + str(v) + "%</font>")
#         else:
#             index.append("<font color='green'>" + str(v) + "%</font>")
#     ret = f'7. 中国金龙鱼指数ETF盘中{index[0]}，盘后{index[1]}；\n8. 富时中国3倍做多ETF盘中{index[2]}，盘后{index[3]}\n'
#     return ret

stocks = ['105.PGJ', '107.YINN']
futures = ['101_GC00Y', '104_CN00Y', '112_B00Y']
indexes_pre = ['100.DJIA','100.NDX','100.SPX','100.FTSE','100.GDAXI','100.FCHI','100.UDI',
              '133.USDCNH','107.YINN','105.PGJ','100.N225','100.SENSEX','100.KS11']

indexes_post = ['1.000001','0.399001','0.399006','1.000688','0.899050','100.HSI','100.HSCEI',
               '124.HSTECH','100.N225','100.SENSEX','100.KS11','100.UDI','133.USDCNH','159.ecfi']


def get_future_from_east_money(future):
    #https://futsseapi.eastmoney.com/static/104_CN00Y_qt?callbackName=jQuery35102158605869136534_1741582410930&field=name,sc,dm,p,zsjd,zdf,zde,utime,o,zjsj,qrspj,h,l,mrj,mcj,vol,cclbh,zt,dt,np,wp,ccl,rz,cje,mcl,mrl,jjsj,j,lb,zf&token=1101ffec61617c99be287c1bec3085ff&_=1741582410931
    url = f'https://futsseapi.eastmoney.com/static/{future}_qt?field=name,sc,dm,p,zsjd,zdf,zde,utime,o,zjsj,qrspj,h,l,mrj,mcj,vol,cclbh,zt,dt,np,wp,ccl,rz,cje,mcl,mrl,jjsj,j,lb,zf&token=1101ffec61617c99be287c1bec3085ff'
    r = requests.get(url)
    data_json = r.json()
    if data_json['qt']['zdf'] > 0:
        ret = f"{data_json["qt"]["name"]}<font color='red'>+{data_json["qt"]["zdf"]}%</font>"
    else:
        ret = f"{data_json["qt"]["name"]}<font color='green'>{data_json["qt"]["zdf"]}%</font>"
    print(ret)
    return ret
def get_stock_from_east_money(stock):
    """
    东方财富网-股票
    """
    # https://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=1&cb=jQuery351020199249398057395_1741580656635&fields=f58%2Cf107%2Cf57%2Cf43%2Cf59%2Cf169%2Cf170%2Cf152%2Cf46%2Cf60%2Cf44%2Cf45%2Cf47%2Cf48%2Cf19%2Cf532%2Cf39%2Cf161%2Cf49%2Cf171%2Cf50%2Cf86%2Cf600%2Cf601%2Cf154%2Cf84%2Cf85%2Cf168%2Cf108%2Cf116%2Cf167%2Cf164%2Cf92%2Cf71%2Cf117%2Cf292%2Cf301&secid=105.PGJ&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&dect=1&_=1741580656636
    url = "http://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fltt": "1",
        "invt": "2",
        "secid": stock,
        "fields": "f58,f107,f57,f43,f59,f169,f170,f152,f46,f60,f44,f45,f47,f48,f19,f532,f39,f161,f49,f171,f50,f86,f600,f601,f154,f84,f85,f168,f108,f116,f167,f164,f92,f71,f117,f292,f301"
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if data_json['data']['f170'] > 0:
        ret = f"{data_json["data"]["f58"]}<font color='red'>+{round(data_json["data"]["f170"] / 100, 2)}%</font>"
    else:
        ret = f"{data_json["data"]["f58"]}<font color='green'>{round(data_json["data"]["f170"] / 100, 2)}%</font>"
    print(ret)
    return ret

def get_index_from_east_money(indexes):
    """
    东方财富网-指数
    """
    # https://push2.eastmoney.com/api/qt/ulist/get?fltt=1&invt=2&cb=jQuery35103528774634350651_1741574753128&fields=f12,f13,f14,f1,f2,f4,f3,f152,f6,f104,f105,f106&secids=1.000001,0.399001&ut=fa5fd1943c7b386f172d6893dbfba10b&pn=1&np=1&pz=20&dect=1&wbp2u=%7C0%7C0%7C0%7Cweb&_=1741574753179
    url = "http://push2.eastmoney.com/api/qt/ulist/get"
    ids = ''
    for index in indexes:
        ids += index + ','
    ids = ids[:-1]
    params = {
        "pn": 1,
        "pz": len(indexes),
        "po": "1",
        "np": "1",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fltt": "1",
        "invt": "2",
        "secids": ids,
        "fields": "f12,f13,f14,f1,f2,f4,f3,f152,f6,f104,f105,f106",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    ret = []
    for item in data_json['data']['diff']:
        if item['f3'] > 0:
            ret.append(f"{item['f14']}<font color='red'>+{round(item['f3'] / 100, 2)}%</font>")
        else:
            ret.append(f"{item['f14']}<font color='green'>{round(item['f3'] / 100, 2)}%</font>")
    print(ret)
    return ret

def get_news():
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--enable-unsafe-swiftshader')

    # 设置 ChromeDriver 路径，请替换为你实际的路径
    chromedriver_path = '/usr/bin/chromedriver'
    service = Service(chromedriver_path)

    # 创建浏览器实例
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 财联社 24 小时电报页面 URL
    url = 'https://www.cls.cn/telegraph'
    
    ret = ''

    try:
        # 打开网页
        driver.get(url)
        # 等待页面加载，可根据实际情况调整等待时间
        wait = WebDriverWait(driver, 5)  # 设置最长等待时间为10秒
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "telegraph-list")))
        
        element = driver.find_element(By.CLASS_NAME, "list-more-button")
        element.click()
        time.sleep(1)
        for i in range(0, 3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        # 获取页面源代码
        page_source = driver.page_source

        etree_html = etree.HTML(page_source)
        telegraph_items = etree_html.xpath("//span[@class='c-34304b']/*/text()")
        telegraph_items += etree_html.xpath("//span[@class='c-de0422']/*/text()")
        for item in telegraph_items:
            item = str(item)
            pos1 = item.find("【")
            pos2 = item.find("】")
            if pos1 != -1 and pos2 != -1:
                # 有标题取标题
                item = item[pos1 + 1:pos2]
            else:
                # 没有标题取第一句
                pos1 = 0
                pos2 = item.find("。")
                item = item[pos1:pos2]
            ret += f'- {item}；\n'

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭浏览器
        driver.quit()
    return ret

flag = 0

if len(sys.argv) > 1:
    flag = int(sys.argv[1])

if flag == 0:
    title = "盘前速知"
else:
    title = "盘后速知"

fileName = title + datetime.now().strftime("-%Y-%m-%d") + ".md"
print(fileName)

# config = Config.from_env()
# ctx = QuoteContext(config)

# with open(fileName, 'w') as file:
#     file.write("## 内容仅供参考，不作投资建议。\n")
#     if flag == 0:
#         file.write("### 一. 盘前数据\n")
#         file.write(get_us_index(ctx))
#         file.write("2. 英国富时收<font color='green'>-0.83%</font>，德国DAX收<font color='red'>+1.47%</font>， 法国CAC收<font color='red'>+0.29%</font>；\n")
#         file.write("3. 伦敦金跌<font color='green'>-0.28%</font>，现跌<font color='green'>-0.18%</font>；\n")
#         file.write("4. 美元指数最低<font color='green'>-0.23%</font>；\n")
#         file.write("5. 离岸人民币(兑美元)跌<font color='green'>+0.09%</font>，现跌<font color='green'>+0.02%</font>；\n")
#         file.write("6. 富时A50跌<font color='green'>-1.10%</font>，现涨<font color='red'>+0.31%</font>；\n")
#         file.write(get_us_china_index(ctx))
#         file.write("9. 日经225指数开盘跌<font color='green'>-1.31%</font>,韩国KOSPI指数开盘跌<font color='green'>-1%</font>，日经现价<font color='green'>-2.02%</font>；\n")
#         file.write("10. 布油涨<font color='red'>+0.17%</font>；\n")
#         file.write("### 二. 盘前快讯\n")
#         file.write(get_news())
#         file.write("### 三. 盘前影响\n")
#         file.write("### 四. 盘前策略\n")
#         file.write("## 先看后赞养成习惯，留言收藏人生辉煌\n")
#     else:
#         file.write("### 一. 盘后数据\n")
#         file.write(get_china_index(ctx))
#         file.write(get_hk_index(ctx))
#         file.write("3. 日经<font color='red'>+0.77%</font>；\n")
#         file.write("4. 离岸人民币<font color='red'>+0.08%</font>；\n")
#         file.write("5. 富时A50<font color='red'>+0.96%</font>；\n")
#         file.write("6. 欧线集运指数<font color='red'>+11.53%</font>。\n")
#         file.write("### 二. 盘后快讯\n")
#         file.write(get_news())
#         file.write("### 三. 复盘\n")
#         file.write("### 四. 今日感悟\n")
#         file.write("## 先看后赞养成习惯，留言收藏人生辉煌\n")
#     file.close()

with open(fileName, 'w') as file:
    file.write("## 内容仅供参考，不作投资建议。\n")
    if flag == 0:
        file.write("### 一. 盘前数据\n")
        indexes = get_index_from_east_money(indexes_pre)
        i = 1
        for index in indexes:
            file.write(f'{i}. {index}；\n')
            i += 1
        for future in futures:
            future = get_future_from_east_money(future)
            file.write(f'{i}. {future}；\n')
            i += 1
        file.write("### 二. 盘前快讯\n")
        file.write(get_news())
        file.write("### 三. 盘前影响\n")
        file.write("### 四. 盘前策略\n")
        file.write("## 先看后赞养成习惯，留言收藏人生辉煌\n")
    else:
        file.write("### 一. 盘后数据\n")
        indexes = get_index_from_east_money(indexes_post)
        i = 1
        for index in indexes:
            file.write(f'{i}. {index}；\n')
            i += 1
        for future in futures:
            future = get_future_from_east_money(future)
            file.write(f'{i}. {future}；\n')
            i += 1
        file.write("### 二. 盘后快讯\n")
        file.write(get_news())
        file.write("### 三. 复盘\n")
        file.write("### 四. 今日感悟\n")
        file.write("## 先看后赞养成习惯，留言收藏人生辉煌\n")
    file.close()