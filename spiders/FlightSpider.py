# import time
# import random
# import urllib.parse
# import scrapy
# import logging
# import os
# import re
# import json
# from selenium import webdriver
# from selenium.webdriver.edge.service import Service as EdgeService
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from scrapy.http import HtmlResponse
#
# class FliggySpider(scrapy.Spider):
#     name = "fliggy"  # 爬虫名称必须唯一
#     allowed_domains = ["sjipiao.fliggy.com"]
#
#     def __init__(self, depCity=None, arrCity=None, depDate=None, *args, **kwargs):
#         super(FliggySpider, self).__init__(*args, **kwargs)
#         self.depCity = depCity
#         self.arrCity = arrCity
#         self.depDate = depDate
#
#         # 设置 Edge Driver 路径
#         driver_path = 'E:/Spider/msedgedriver.exe'  # 替换为实际路径
#         edge_options = webdriver.EdgeOptions()
#         # edge_options.add_argument("--headless")  # 可选：无头模式
#         self.driver = webdriver.Edge(service=EdgeService(driver_path), options=edge_options)
#
#     def generate_url(self):
#         """
#         动态生成请求 URL。
#         """
#         try:
#             if not all([self.depCity, self.arrCity, self.depDate]):
#                 raise ValueError("Missing required parameters: depCity, arrCity, or depDate")
#
#             user_agent = self.driver.execute_script("return navigator.userAgent")
#
# 			# 基础URL
#             base_url = 'https://sjipiao.fliggy.com/searchow/search.htm'
#
#             # 动态生成 callback 和 _ksTS
#             timestamp = int(time.time() * 1000)
#             callback_suffix = timestamp % 1000
#             callback = f"jsonp{callback_suffix}"
#             ksTS = f"{timestamp}_{random.randint(100, 999)}"
#
#             # 动态生成城市名称的 URL 编码
#             depCityName_encoded = urllib.parse.quote(self.airport_code_to_city_name(self.depCity)) if self.depCity else ""
#             arrCityName_encoded = urllib.parse.quote(self.airport_code_to_city_name(self.arrCity)) if self.arrCity else ""
#
#             # 构造查询参数
#             params = {
#                 # '_ksTS': ksTS,
#                 'callback': 'jsonp159',
#                 'tripType': '0',  # 单程
#                 'depCity': self.depCity,
#                 'depCityName': depCityName_encoded,
#                 'arrCity': self.arrCity,
#                 'arrCityName': arrCityName_encoded,
#                 'depDate': self.depDate,
#                 'searchSource': '99',
#                 'sKey': '',
#                 'qid': '',
#                 'needMemberPrice': 'true',
#                 '_input_charset': 'utf-8',
#                 'ua': user_agent,
#                 'itemId': '',
#                 'openCb': 'false'
#             }
#
#             # 构造完整的URL
#             query_string = urllib.parse.urlencode(params)
#             full_url = f"{base_url}?{query_string}"
#             return full_url
#
#         except Exception as e:
#             self.logger.error(f"Error generating URL: {e}")
#             return None
#
#     def start_requests(self):
#         """
#         生成初始请求。
#         """
#         url = self.generate_url()
#         if url:
#             self.logger.info(f"Starting request to URL: {url}")
#             yield scrapy.Request(url=url, callback=self.parse_with_selenium)
#         else:
#             self.logger.error("Failed to generate URL")
#
#     def parse_with_selenium(self, response):
#         """
#         使用 Selenium 处理动态加载的页面内容。
#         """
#         self.logger.info(f"Navigating to URL with Selenium: {response.url}")
#
#         # 使用 Selenium 打开页面
#         self.driver.get(response.url)
#
#         # 等待页面加载完成
#         try:
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "J_FlightListBox"))  # 替换为目标页面的实际元素ID
#             )
#             self.logger.info("Page loaded successfully")
#         except Exception as e:
#             self.logger.error(f"Failed to load page: {e}")
#             return
#
#         # 获取页面源代码
#         page_source = self.driver.page_source
#
#         # 将页面源代码封装为 Scrapy 的 HtmlResponse 对象
#         response = HtmlResponse(url=self.driver.current_url, body=page_source, encoding='utf-8')
#
#         # 提取 JSON 数据部分
#         jsonp_response = response.text.strip()
#         match = re.match(r"^jsonp\d+$(.*)$$", jsonp_response)
#         if not match:
#             self.logger.error("Failed to parse JSONP response")
#             return
#
#         # 将 JSON 数据转换为 Python 字典
#         try:
#             raw_data = json.loads(match.group(1))
#         except json.JSONDecodeError as e:
#             self.logger.error(f"Failed to decode JSON data: {e}")
#             return
#
#         # 提取重要的字段
#         aircode_name_map = raw_data.get("data", {}).get("aircodeNameMap", {})
#         flight_list = raw_data.get("data", {}).get("flight", [])
#
#         # 构造新的字典
#         parsed_data = {"flights": []}
#
#         for flight in flight_list:
#             # 提取航班基本信息
#             flight_info = {
#                 "flightNo": flight.get("flightNo"),
#                 "airline": aircode_name_map.get(flight.get("airlineCode"), "未知"),
#                 "depAirport": flight.get("depAirport"),
#                 "depTime": flight.get("depTime"),
#                 "arrAirport": flight.get("arrAirport"),
#                 "arrTime": flight.get("arrTime"),
#                 "price": flight.get("cabin", {}).get("price"),
#                 "discount": flight.get("cabin", {}).get("discount"),
#                 "bestPrice": flight.get("cabin", {}).get("bestPrice"),
#                 "baggageInfo": [
#                     label.get("text") for label in flight.get("cabin", {}).get("baggageLabels", [])
#                 ],
#                 "hasFood": bool(flight.get("hasFood")),
#                 "stops": flight.get("stop", 0)
#             }
#             parsed_data["flights"].append(flight_info)
#
#         # 保存 JSON 数据到文件
#         self.save_json_to_file(parsed_data)
#
#     def save_json_to_file(self, data):
#         """
#         将 JSON 数据保存为文件。
#         文件路径：项目目录下的 "flight_inf" 文件夹。
#         文件名格式：{self.depCity}_{self.arrCity}_{self.depDate}.json
#         """
#         # 确保 "flight_inf" 文件夹存在
#         folder_name = "flight_inf"
#         if not os.path.exists(folder_name):
#             os.makedirs(folder_name)
#
#         # 构造文件名
#         file_name = f"{self.depCity}_{self.arrCity}_{self.depDate}.json"
#         file_path = os.path.join(folder_name, file_name)
#
#         # 写入 JSON 数据到文件
#         try:
#             with open(file_path, "w", encoding="utf-8") as f:
#                 json.dump(data, f, ensure_ascii=False, indent=4)
#             self.logger.info(f"JSON data saved to: {file_path}")
#         except Exception as e:
#             self.logger.error(f"Failed to save JSON data to file: {e}")
#
#     @staticmethod
#     def airport_code_to_city_name(airport_code):
#         """
#         将机场代码转换为对应的中文城市名称。
#
#         参数:
#             airport_code (str): 机场代码，例如 "SHA", "PVG", "BJS".
#
#         返回:
#             str: 对应的城市名称，如果未找到则返回 '未知' 或者其他提示信息。
#         """
#         # 创建一个包含机场代码和城市名称映射的字典
#         airport_city_map = {
#             "SHA": "上海",   # 上海虹桥国际机场
#             "PVG": "上海",   # 上海浦东国际机场
#             "PEK": "北京",   # 北京首都国际机场
#             "BJS": "北京",   # 北京大兴国际机场也使用 BJS 作为备选代码
#             "CAN": "广州",   # 广州白云国际机场
#             "CTU": "成都",   # 成都双流国际机场
#             "CKG": "重庆",   # 重庆江北国际机场
#             # 可以根据需要添加更多的机场代码和城市名称
#         }
#
#         # 使用 get 方法查找对应的中文城市名称，默认返回 '未知'
#         return airport_city_map.get(airport_code, "未知")
#
#     def closed(self, reason):
#         """
#         当爬虫关闭时，确保关闭 Selenium WebDriver。
#         """
#         self.driver.quit()
#         self.logger.info("Selenium WebDriver closed.")
#
# # airports = [
# #     {
# #         "CityName": "上海",
# #         "City": "SH",
# #         "Airport": {
# #             "上海浦东国际机场": "PVG",
# #             "上海虹桥国际机场": "SHA"
# #         }
# #     },
# #     {
# #         "CityName": "北京",
# #         "City": "BJ",
# #         "Airport": {
# #             "北京首都国际机场": "PEK",
# #             "北京大兴国际机场": "PKX"
# #         }
# #     },
# #     {
# #         "CityName": "广州",
# #         "City": "GZ",
# #         "Airport": {
# #             "广州白云国际机场": "CAN"
# #         }
# #     },
# #     {
# #         "CityName": "深圳",
# #         "City": "SZ",
# #         "Airport": {
# #             "深圳宝安国际机场": "SZX"
# #         }
# #     },
# #     {
# #         "CityName": "成都",
# #         "City": "CD",
# #         "Airport": {
# #             "成都双流国际机场": "CTU",
# #             "成都天府国际机场": "TFU"
# #         }
# #     },
# #     {
# #         "CityName": "重庆",
# #         "City": "CQ",
# #         "Airport": {
# #             "重庆江北国际机场": "CKG"
# #         }
# #     },
# #     {
# #         "CityName": "杭州",
# #         "City": "HZ",
# #         "Airport": {
# #             "杭州萧山国际机场": "HGH"
# #         }
# #     },
# #     {
# #         "CityName": "西安",
# #         "City": "XA",
# #         "Airport": {
# #             "西安咸阳国际机场": "XIY"
# #         }
# #     },
# #     {
# #         "CityName": "昆明",
# #         "City": "KM",
# #         "Airport": {
# #             "昆明长水国际机场": "KMG"
# #         }
# #     },
# #     {
# #         "CityName": "厦门",
# #         "City": "XM",
# #         "Airport": {
# #             "厦门高崎国际机场": "XMN"
# #         }
# #     },
# #     {
# #         "CityName": "南京",
# #         "City": "NJ",
# #         "Airport": {
# #             "南京禄口国际机场": "NKG"
# #         }
# #     },
# #     {
# #         "CityName": "武汉",
# #         "City": "WH",
# #         "Airport": {
# #             "武汉天河国际机场": "WUH"
# #         }
# #     },
# #     {
# #         "CityName": "长沙",
# #         "City": "CS",
# #         "Airport": {
# #             "长沙黄花国际机场": "CSX"
# #         }
# #     },
# #     {
# #         "CityName": "青岛",
# #         "City": "QD",
# #         "Airport": {
# #             "青岛流亭国际机场": "TAO",  # 注意: 流亭机场已关闭, 新的胶东国际机场IATA代码也是TAO
# #             "青岛胶东国际机场": "TAO"   # 请根据实际情况调整
# #         }
# #     },
# #     {
# #         "CityName": "大连",
# #         "City": "DL",
# #         "Airport": {
# #             "大连周水子国际机场": "DLC"
# #         }
# #     },
# #     {
# #         "CityName": "海口",
# #         "City": "HK",
# #         "Airport": {
# #             "海口美兰国际机场": "HAK"
# #         }
# #     },
# #     {
# #         "CityName": "三亚",
# #         "City": "SY",
# #         "Airport": {
# #             "三亚凤凰国际机场": "SYX"
# #         }
# #     },
# #     # 更多城市...
# # ]


import scrapy
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from selenium import webdriver
# from urllib.parse import urlencode

import time
import random
import urllib.parse
import scrapy
import logging
import os
import re
import json

from datetime import datetime, timedelta

class FliggySpider(scrapy.Spider):
    name = 'fliggy'
    allowed_domains = ["sjipiao.fliggy.com"]

    # # 获取当前时间戳
    # current_time = time.time()
    # # 加一天的时间戳（1天 = 86400秒）
    # tomorrow_time = current_time + 86400
    # # 转换为本地时间结构
    # local_time = time.localtime(tomorrow_time)
    # # 格式化日期
    # formatted_tomorrow = time.strftime("%Y-%m-%d", local_time)
    #
    # start_urls = [f'https://sjipiao.fliggy.com/homeow/trip_flight_search.htm?searchBy=&ttid=&tripType=0&depCityName=%C9%CF%BA%A3&depCity=&arrCityName=%B1%B1%BE%A9&arrCity=&depDate={formatted_tomorrow}&arrDate=']  # 替换为目标网站的URL
    # print(start_urls)

    # 疑惑：为什么上面的url爬不到，下面的就能爬到？

    # 获取今天的日期
    today = datetime.today()
    # 计算明天的日期
    tomorrow = today + timedelta(days=1)
    # 格式化日期
    formatted_tomorrow = tomorrow.strftime("%Y-%m-%d")
    # print("明天的日期:", formatted_tomorrow)
    start_urls = [f'https://sjipiao.fliggy.com/homeow/trip_flight_search.htm?searchBy=&ttid=&tripType=0&depCityName=%C9%CF%BA%A3&depCity=&arrCityName=%B1%B1%BE%A9&arrCity=&depDate={formatted_tomorrow}&arrDate=']  # 替换为目标网站的URL
    # print(start_urls)

    # start_urls = [f'https://sjipiao.fliggy.com/homeow/trip_flight_search.htm?searchBy=&ttid=&tripType=0&depCityName=%C9%CF%BA%A3&depCity=&arrCityName=%B1%B1%BE%A9&arrCity=&depDate={formatted_tomorrow}&arrDate=']  # 替换为目标网站的URL
    # print(start_urls)
    # # start_urls = [
    # #     'https://sjipiao.fliggy.com/homeow/trip_flight_search.htm?searchBy=&ttid=&tripType=0&depCityName=%C9%CF%BA%A3&depCity=&arrCityName=%B1%B1%BE%A9&arrCity=&depDate=2025-03-26&arrDate=']  # 替换为目标网站的URL




    def __init__(self, depCity=None, arrCity=None, depDate=None, *args, **kwargs):
        super(FliggySpider, self).__init__(*args, **kwargs)
        self.depCity = depCity
        self.arrCity = arrCity
        self.depDate = depDate
        # arrDate

        # 设置 Edge Driver 路径
        driver_path = 'E:/Spider/msedgedriver.exe'  # 替换为实际路径
        edge_options = webdriver.EdgeOptions()
        # edge_options.add_argument("--headless")  # 可选：无头模式
        self.driver = webdriver.Edge(service=Service(driver_path), options=edge_options)


        # self.start_urls = [self.generate_start_url()]  # 替换为目标网站的URL

    # def start_requests(self):
    #     """
    #     生成初始请求。
    #     """
    #     # url = self.generate_start_url()
    #     url = ['https://sjipiao.fliggy.com/homeow/trip_flight_search.htm?searchBy=&ttid=&tripType=0&depCityName=%C9%CF%BA%A3&depCity=&arrCityName=%B1%B1%BE%A9&arrCity=&depDate=2025-04-20&arrDate=']  # 替换为目标网站的URL
    #
    #     if url:
    #         self.logger.info(f"Starting request to URL: {url}")
    #         return scrapy.Request(url=url, callback=self.parse)
    #     else:
    #         self.logger.error("Failed to generate URL")

    def parse(self, response):
        self.driver.get(response.url)

        # 等待某个元素加载完成作为页面已加载的标志，根据实际情况调整
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "J_FlightListBox"))  # 替换成页面上的某个元素ID或其它定位方式
            )
            print("页面加载完成")
        except Exception as e:
            print(f"页面加载失败: {e}")
            return

        full_url = self.generate_url()

        self.driver.get(full_url)

        # 获取页面HTML源码
        page_source = self.driver.page_source

        # 将页面源代码封装为 Scrapy 的 HtmlResponse 对象
        response = HtmlResponse(url=self.driver.current_url, body=page_source, encoding='utf-8')

        # 提取 JSON 数据部分
        jsonp_response = response.text.strip()
        # jsonp_response = self.driver.page_source
        self.save_json_to_file(jsonp_response, "raw")

        match = re.search(r'jsonp\d+\((.*?)\)', jsonp_response)
        if not match:
            self.logger.error("Failed to parse JSONP response")
            return

        # 将 JSON 数据转换为 Python 字典
        try:
            json_data_escaped = match.group(1).strip("\"").replace("\\\"", "\"")
            print(json_data_escaped)
            raw_data = json.loads(json_data_escaped)

            # 提取重要的字段
            aircode_name_map = raw_data.get("data", {}).get("aircodeNameMap", {})
            flight_list = raw_data.get("data", {}).get("flight", [])

            # 构造新的字典
            parsed_data = {"flights": []}

            for flight in flight_list:
                # 提取航班基本信息
                flight_info = {
                    "flightNo": flight.get("flightNo"),
                    "airline": aircode_name_map.get(flight.get("airlineCode"), "未知"),
                    "depAirport": flight.get("depAirport"),
                    "depTime": flight.get("depTime"),
                    "arrAirport": flight.get("arrAirport"),
                    "arrTime": flight.get("arrTime"),
                    "price": flight.get("cabin", {}).get("price"),
                    "discount": flight.get("cabin", {}).get("discount"),
                    "bestPrice": flight.get("cabin", {}).get("bestPrice"),
                    "baggageInfo": [
                        label.get("text") for label in flight.get("cabin", {}).get("baggageLabels", [])
                    ],
                    "hasFood": bool(flight.get("hasFood")),
                    "stops": flight.get("stop", 0)
                }
                parsed_data["flights"].append(flight_info)

            # 保存 JSON 数据到文件
            self.save_json_to_file(parsed_data)


        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON data: {e}")
            return


    def save_json_to_file(self, data, tag=None):
        """
        将 JSON 数据保存为文件。
        文件路径：项目目录下的 "flight_inf" 文件夹。
        文件名格式：{self.depCity}_{self.arrCity}_{self.depDate}.json
        """
        # 确保 "flight_inf" 文件夹存在
        folder_name = "flight_inf"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # 构造文件名
        tag = f"_{tag}" if tag else ""
        file_name = f"{self.depCity}_{self.arrCity}_{self.depDate}{tag}.json"
        file_path = os.path.join(folder_name, file_name)

        # 写入 JSON 数据到文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.logger.info(f"JSON data saved to: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save JSON data to file: {e}")

    @staticmethod
    def airport_code_to_city_name(airport_code):
        """
        将机场代码转换为对应的中文城市名称。

        参数:
            airport_code (str): 机场代码，例如 "SHA", "PVG", "BJS".

        返回:
            str: 对应的城市名称，如果未找到则返回 '未知' 或者其他提示信息。
        """
        # 创建一个包含机场代码和城市名称映射的字典
        airport_city_map = {
            "SHA": "上海",  # 上海虹桥国际机场
            "PVG": "上海",  # 上海浦东国际机场
            "PEK": "北京",  # 北京首都国际机场
            "BJS": "北京",  # 北京大兴国际机场也使用 BJS 作为备选代码
            "CAN": "广州",  # 广州白云国际机场
            "CTU": "成都",  # 成都双流国际机场
            "CKG": "重庆",  # 重庆江北国际机场
            # 可以根据需要添加更多的机场代码和城市名称
        }

        # 使用 get 方法查找对应的中文城市名称，默认返回 '未知'
        return airport_city_map.get(airport_code, "未知")

    def closed(self, reason):
        """
        当爬虫关闭时，确保关闭 Selenium WebDriver。
        """
        self.driver.quit()
        self.logger.info("Selenium WebDriver closed.")


    def generate_start_url(self):
        """
        动态生成航班搜索页面的 URL。
        """
        try:
            if not all([self.depCity, self.arrCity, self.depDate]):
                raise ValueError("Missing required parameters: depCity, arrCity, or depDate")

            # 基础 URL
            base_url = 'https://sjipiao.fliggy.com/homeow/trip_flight_search.htm'

            # 动态生成城市名称的 URL 编码
            depCityName_encoded = urllib.parse.quote(
                self.airport_code_to_city_name(self.depCity)) if self.depCity else ""
            arrCityName_encoded = urllib.parse.quote(
                self.airport_code_to_city_name(self.arrCity)) if self.arrCity else ""

            # 构造查询参数
            params = {
                'searchBy': '',  # 搜索方式（空字符串表示默认）
                'ttid': '',  # 不清楚具体含义，保持为空
                'tripType': '0',  # 单程
                'depCityName': depCityName_encoded,  # 出发城市名称（URL 编码）
                'depCity': self.depCity,  # 出发城市代码
                'arrCityName': arrCityName_encoded,  # 到达城市名称（URL 编码）
                'arrCity': self.arrCity,  # 到达城市代码
                'depDate': self.depDate,  # 出发日期
                'arrDate': '',  # 返回日期（如果为空则设为空字符串）self.arrDate or
            }

            # 构造完整的 URL
            query_string = urllib.parse.urlencode(params)
            full_url = f"{base_url}?{query_string}"
            return full_url

        except Exception as e:
            print(f"Error generating URL: {e}")
            return None

    def generate_url(self):
        """
        动态生成请求 URL。
        """
        try:
            if not all([self.depCity, self.arrCity, self.depDate]):
                raise ValueError("Missing required parameters: depCity, arrCity, or depDate")

            user_agent = self.driver.execute_script("return navigator.userAgent")

            # 基础URL
            base_url = 'https://sjipiao.fliggy.com/searchow/search.htm'

            # # 动态生成 callback 和 _ksTS
            # timestamp = int(time.time() * 1000)
            # callback_suffix = timestamp % 1000
            # callback = f"jsonp{callback_suffix}"
            # ksTS = f"{timestamp}_{random.randint(100, 999)}"

            # 动态生成城市名称的 URL 编码
            depCityName_encoded = urllib.parse.quote(
                self.airport_code_to_city_name(self.depCity)) if self.depCity else ""
            arrCityName_encoded = urllib.parse.quote(
                self.airport_code_to_city_name(self.arrCity)) if self.arrCity else ""

            # 构造查询参数
            params = {
                # '_ksTS': ksTS,
                'callback': 'jsonp159',
                'tripType': '0',  # 单程
                'depCity': self.depCity,
                'depCityName': depCityName_encoded,
                'arrCity': self.arrCity,
                'arrCityName': arrCityName_encoded,
                'depDate': self.depDate,
                'searchSource': '99',
                'sKey': '',
                'qid': '',
                'needMemberPrice': 'true',
                '_input_charset': 'utf-8',
                'ua': user_agent,
                'itemId': '',
                'openCb': 'false'
            }

            # 构造完整的URL
            query_string = urllib.parse.urlencode(params)
            full_url = f"{base_url}?{query_string}"
            return full_url

        except Exception as e:
            self.logger.error(f"Error generating URL: {e}")
            return None

