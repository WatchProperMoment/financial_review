# -*- coding: utf-8 -*-
import os
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
import re
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
import os
from openai import OpenAI

def get_refine_news_from_ai(news, client):
    prompt_1 = f"""
        执行以下操作：
        1-重新整理下面用三个反引号括起来的文本。
        2-去除重复的内容。
        3-去除与财经无关的内容。
        4-如果该条目对股票市场有显著影响，请在该条目前缀<font color='red'>，后缀</font>
        5-对内容润色。
        6-按原格式输出，但去除三个反引号
        7-不要说明处理步骤
        ```{news}```
        """
    completion = client.chat.completions.create(
        model="qwen-plus", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt_1}],
        )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def get_effect_from_ai(indexs, client):
    format_1 = f"""
        1. 短期情绪消极:中国金龙鱼指数ETF和富时中国3倍做多ETF大跌，可能引导A股和港股低开;
        2. 内外市场联动逻辑：道指<font color='green'>-0.84%</font>,纳指<font color='green'>-2.15%</font>,标普500指数<font color='green'>-1.57%</font>,英国富时100<font color='green'>-1.57%</font>,德国DAX30<font color='green'>-1.57%</font>,法国CAC40<font color='green'>-1.57%</font>外盘短线情绪消极，可能引导A股和港股低开；
        3. 股指期货影响：A50期指当月连续大跌，可能引导A股低开;恒生期货主连大跌，可能引导港股低开;
    """
    prompt_1 = f"""
        执行以下操作：
        1-请根据三个反引号括起来的文本信息判断对今天A股市场和港股市场开盘的影响。
        2-根据三个反引号括起来的文本信息中的数值，应该突出强调暴跌、大跌、微跌、暴涨、大涨、微涨。
        3-使用下面<>中的示例格式编辑输出，但不要保留前后的<>。
        4-暴涨、大涨、微涨则需要将green替换成red。
        5-不要说明处理步骤
        ```{indexs}```
        <{format_1}>
        """
    completion = client.chat.completions.create(
        model="qwen-plus", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt_1}],
        )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
class GenerateArticle:
    def __init__(self):
        self.china_ratio = 0
        self.china_3_long_ratio = 0
        self.future_a50 = 0
        self.future_hsi = 0
        self.DJIA_ratio = 0
        self.NDX_ratio = 0
        self.SPX_ratio = 0
        self.FTSE_ratio = 0
        self.GDAXI_ratio = 0
        self.FCHI_ratio = 0
        self.us_market_news = ''
        self.effect_indexs = ''

    def get_future_from_east_money(self, future):
        #https://futsseapi.eastmoney.com/static/104_CN00Y_qt?callbackName=jQuery35102158605869136534_1741582410930&field=name,sc,dm,p,zsjd,zdf,zde,utime,o,zjsj,qrspj,h,l,mrj,mcj,vol,cclbh,zt,dt,np,wp,ccl,rz,cje,mcl,mrl,jjsj,j,lb,zf&token=1101ffec61617c99be287c1bec3085ff&_=1741582410931
        url = f'https://futsseapi.eastmoney.com/static/{future}_qt?field=name,sc,dm,p,zsjd,zdf,zde,utime,o,zjsj,qrspj,h,l,mrj,mcj,vol,cclbh,zt,dt,np,wp,ccl,rz,cje,mcl,mrl,jjsj,j,lb,zf&token=1101ffec61617c99be287c1bec3085ff'
        r = requests.get(url)
        data_json = r.json()
        if future == '104_CN00Y':
            self.future_a50 = data_json["qt"]["zdf"] * 100
        if data_json['qt']['zdf'] > 0:
            ret = f"{data_json["qt"]["name"]}: <font color='red'>{data_json["qt"]["p"]}(+{round(data_json["qt"]["p"] - data_json["qt"]["qrspj"], 2)}/+{data_json["qt"]["zdf"]}%)</font>"
        else:
            ret = f"{data_json["qt"]["name"]}: <font color='green'>{data_json["qt"]["p"]}({round(data_json["qt"]["p"] - data_json["qt"]["qrspj"], 2)}/{data_json["qt"]["zdf"]}%)</font>"
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

    def get_index_from_east_money(self, indexes):
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
            can_use = True
            if item['f12'] == 'YINN':
                item['f14'] = '富时中国3倍做多ETF'
            elif item['f12'] == 'PGJ':
                item['f14'] = '中国金龙鱼指数ETF'
            elif item['f12'] == 'DJIA':
                pass
            elif item['f12'] == 'NDX':
                pass
            elif item['f12'] == 'SPX':
                pass
            elif item['f12'] == 'FTSE':
                pass
            elif item['f12'] == 'GDAXI':
                pass
            elif item['f12'] == 'FCHI':
                pass
            elif item['f12'] == 'HSI_M':
                pass
            else:
                can_use = False
            if re.match(r'^-?\d+$', str(item['f3'])):
                v = int(item['f3'])
            else:
                v = 0
            if v > 0:
                s = f"{item['f14']}: <font color='red'>{round(item['f2'] / 100, 2)}(+{round(item['f4'] / 100, 2)}/+{round(v / 100, 2)}%)</font>"
            else:
                s = f"{item['f14']}: <font color='green'>{round(item['f2'] / 100, 2)}({round(item['f4'] / 100, 2)}/{round(v / 100, 2)}%)</font>"
            ret.append(s)
            if can_use:
                self.effect_indexs += s
        print(ret)
        return ret

    def get_up_down_from_cls(self):
        """
        财联社-指数
        """
        # https://x-quote.cls.cn/quote/index/home?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737
        url = "https://x-quote.cls.cn/quote/index/home"
        params = {
            "app": "CailianpressWeb",
            "os": "web",
            "sv": "8.4.6",
            "sign": "9f8797a1f4de66c2370f7a03990d2737"
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        ret = f"涨跌停比<font color='red'>{data_json['data']['up_down_dis']['up_num']}</font>:<font color='green'>{data_json['data']['up_down_dis']['down_num']}</font>"
        print(ret)
        return ret

    def get_balance_from_cls(self):
        """
        """
        # https://x-quote.cls.cn/v2/quote/a/stock/emotion?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737
        url = "https://x-quote.cls.cn/v2/quote/a/stock/emotion"
        params = {
            "app": "CailianpressWeb",
            "os": "web",
            "sv": "8.4.6",
            "sign": "9f8797a1f4de66c2370f7a03990d2737"
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        ret = f"两市成交<font color='red'>{data_json['data']['shsz_balance']}</font>，"
        if data_json['data']['shsz_balance_change_px'].startswith('-'):
            ret += f"较上一交易日<font color='green'>{data_json['data']['shsz_balance_change_px']}</font>，"
        else:
            ret += f"较上一交易日<font color='red'>{data_json['data']['shsz_balance_change_px']}</font>，"
        ret += f"<font color='red'>{data_json['data']['up_down_dis']['rise_num']}</font>家上涨，<font color='green'>{data_json['data']['up_down_dis']['fall_num']}</font>家下跌，"
        return ret

    def get_news(self, blacklist, client):
        # 设置 Chrome 浏览器选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--enable-unsafe-swiftshader')

        # 设置 ChromeDriver 路径，请替换为你实际的路径
        # chromedriver_path = 'D:\\software\\chrome-headless-shell-win64\\chromedriver.exe'
        # service = Service(chromedriver_path)

        # 创建浏览器实例
        driver = webdriver.Chrome(options=chrome_options)

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
            for i in range(0, 5):
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
                for bl in blacklist:
                    if item.find(bl) != -1:
                        item = ''
                        break
                if item.find('标普500指数') != -1:
                    us_market_news = item
                    item = ''
                if len(item) > 1:
                    fchar = item[0]
                    schar = item[1]
                    if (fchar >= u'\u2460' and fchar <= u'\u2480'):
                        item = item[1:]
                    if fchar.isnumeric() and (schar == '、' or schar == '.'):
                        item = item[2:]
                    fchar = item[0:2]
                    schar = item[2]
                    if fchar.isnumeric() and (schar == '、' or schar == '.'):
                        item = item[3:]
                    if item.startswith('财联社'):
                        pos = item.find('，')
                        item = item[pos + 1:]
                    ret += f'- {item}；\n'

        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            # 关闭浏览器
            driver.quit()
        with open('temp.md', 'w', encoding='utf-8') as file:
            file.write(ret)
            file.close()
        return get_refine_news_from_ai(ret, client)
        
stocks = ['105.PGJ', '107.YINN']
futures = ['101_GC00Y', '104_CN00Y', '112_B00Y']
indexes_pre = ['100.DJIA','100.NDX','100.SPX','100.FTSE','100.GDAXI','100.FCHI','100.UDI',
            '133.USDCNH','107.YINN','105.PGJ','100.N225','100.SENSEX','100.KS11', '134.HSI_M']

indexes_post = ['1.000001','0.399001','0.399006','1.000688','0.899050','100.HSI','100.HSCEI',
            '124.HSTECH','100.N225','100.SENSEX','100.KS11','100.UDI','133.USDCNH','159.ecfi', '134.HSI_M']

black_list = ["也门", "新股", "冲突", "知情人", "评级", "据传", "乌克兰", "俄罗斯", ".HK", "涨停", "跌停", "跟涨", "跟跌", "现涨", "现跌", "跌超", "涨超", "恒生指数", "公告", "年报", "朝鲜", "以色列", "胡塞", "财联社盯盘", "星矿数据", "南向资金"] 

def main():
    flag = 0
    if len(sys.argv) > 1:
        flag = int(sys.argv[1])

    if flag == 0:
        title = "盘前速知"
    else:
        title = "盘后速知"
        
    ga = GenerateArticle()
    
    fileName = title + datetime.now().strftime("-%Y-%m-%d") + ".md"
    print(fileName)
    
    fileName = os.path.join("articles", fileName)

    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"), 
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    with open(fileName, 'w', encoding='utf-8') as file:
        file.write("## 内容仅供参考，不作投资建议。\n")
        if flag == 0:
            file.write("### 一. 盘前数据\n")
            indexes = ga.get_index_from_east_money(indexes_pre)
            i = 1
            for index in indexes:
                file.write(f'{i}. {index}；\n')
                i += 1
            for future in futures:
                future_ret = ga.get_future_from_east_money(future)
                if future == '104_CN00Y':
                    ga.effect_indexs += future_ret
                file.write(f'{i}. {future_ret}；\n')
                i += 1
            file.write("### 二. 盘前快讯<AI整理润色>\n")
            file.write(ga.get_news(black_list, client))
            file.write("\n### 三. 盘前影响<AI整理润色>\n")
            file.write(get_effect_from_ai(ga.effect_indexs, client))
            file.write("\n### 四. 盘前策评\n")
        else:
            file.write("### 一. 盘后数据\n")
            indexes = ga.get_index_from_east_money(indexes_post)
            i = 1
            for index in indexes:
                file.write(f'{i}. {index}；\n')
                i += 1
            for future in futures:
                future = ga.get_future_from_east_money(future)
                file.write(f'{i}. {future}；\n')
                i += 1
            file.write("### 二. 盘后快讯<AI整理润色>\n")
            file.write(ga.get_news(black_list, client))
            file.write("\n### 三. 复盘\n")
            file.write(ga.get_balance_from_cls() + ga.get_up_down_from_cls() + '\n')
            file.write("### 四. 今日感悟\n")
        file.write("### 公众号文章和模板生成脚本已收录在\n")
        file.write("https://github.com/WatchProperMoment/financial_review\n")
        file.write("> 个人帐号每天只能推送一次，设为星标，可以及时收到更新通知。\n")
        file.write("## 先看后赞养成习惯，留言收藏人生辉煌\n")
        file.close()


if __name__ == "__main__":
    main()
