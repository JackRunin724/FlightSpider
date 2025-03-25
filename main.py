from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.FlightSpider import FliggySpider

def run_spider(depCity, arrCity, depDate):
    """
    启动 FliggySpider 爬虫，并传递参数。
    :param depCity: 出发城市代码（如 SHA）
    :param arrCity: 到达城市代码（如 BJS）
    :param depDate: 出发日期（格式：YYYY-MM-DD）
    """
    # 获取 Scrapy 项目的设置
    settings = get_project_settings()

    # 创建 CrawlerProcess 实例
    process = CrawlerProcess(settings)

    # 将参数传递给爬虫
    process.crawl(FliggySpider, depCity=depCity, arrCity=arrCity, depDate=depDate)

    # 启动爬虫
    process.start()

if __name__ == "__main__":
    # 示例调用

    # # 班次很少的机场
    # run_spider(depCity="CIF", arrCity="NNY", depDate="2025-04-25")
    # 班次比较多的机场
    run_spider(depCity="BJS", arrCity="SHA", depDate="2025-04-25")




# airports = [
#     {
#         "CityName": "上海",
#         "City": "SH",
#         "Airport": {
#             "上海浦东国际机场": "PVG",
#             "上海虹桥国际机场": "SHA"
#         }
#     },
#     {
#         "CityName": "北京",
#         "City": "BJ",
#         "Airport": {
#             "北京首都国际机场": "PEK",
#             "北京大兴国际机场": "PKX"
#         }
#     },
#     {
#         "CityName": "广州",
#         "City": "GZ",
#         "Airport": {
#             "广州白云国际机场": "CAN"
#         }
#     },
#     {
#         "CityName": "深圳",
#         "City": "SZ",
#         "Airport": {
#             "深圳宝安国际机场": "SZX"
#         }
#     },
#     {
#         "CityName": "成都",
#         "City": "CD",
#         "Airport": {
#             "成都双流国际机场": "CTU",
#             "成都天府国际机场": "TFU"
#         }
#     },
#     {
#         "CityName": "重庆",
#         "City": "CQ",
#         "Airport": {
#             "重庆江北国际机场": "CKG"
#         }
#     },
#     {
#         "CityName": "杭州",
#         "City": "HZ",
#         "Airport": {
#             "杭州萧山国际机场": "HGH"
#         }
#     },
#     {
#         "CityName": "西安",
#         "City": "XA",
#         "Airport": {
#             "西安咸阳国际机场": "XIY"
#         }
#     },
#     {
#         "CityName": "昆明",
#         "City": "KM",
#         "Airport": {
#             "昆明长水国际机场": "KMG"
#         }
#     },
#     {
#         "CityName": "厦门",
#         "City": "XM",
#         "Airport": {
#             "厦门高崎国际机场": "XMN"
#         }
#     },
#     {
#         "CityName": "南京",
#         "City": "NJ",
#         "Airport": {
#             "南京禄口国际机场": "NKG"
#         }
#     },
#     {
#         "CityName": "武汉",
#         "City": "WH",
#         "Airport": {
#             "武汉天河国际机场": "WUH"
#         }
#     },
#     {
#         "CityName": "长沙",
#         "City": "CS",
#         "Airport": {
#             "长沙黄花国际机场": "CSX"
#         }
#     },
#     {
#         "CityName": "青岛",
#         "City": "QD",
#         "Airport": {
#             "青岛流亭国际机场": "TAO",  # 注意: 流亭机场已关闭, 新的胶东国际机场IATA代码也是TAO
#             "青岛胶东国际机场": "TAO"   # 请根据实际情况调整
#         }
#     },
#     {
#         "CityName": "大连",
#         "City": "DL",
#         "Airport": {
#             "大连周水子国际机场": "DLC"
#         }
#     },
#     {
#         "CityName": "海口",
#         "City": "HK",
#         "Airport": {
#             "海口美兰国际机场": "HAK"
#         }
#     },
#     {
#         "CityName": "三亚",
#         "City": "SY",
#         "Airport": {
#             "三亚凤凰国际机场": "SYX"
#         }
#     },
#     # 更多城市...
# ]