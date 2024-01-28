import requests
import re
from plugins import register, Plugin, Event, logger

class ReplyType:
    TEXT = 1
    IMAGE = 2

class Reply:
    def __init__(self, reply_type, content):
        self.type = reply_type
        self.content = content  # 文本内容或图片URL存储在这里

@register
class NewsHub(Plugin):
    name = "news_hub"
    
    def __init__(self, config):
        super().__init__(config)
        self.token = self.config.get("token")
        self.weather_city_re = re.compile(r"^(.*?)今天天气怎么样$")

    def will_generate_reply(self, event: Event):
        query = event.message.content.strip()
        if "今天天气怎么样" in query:
            city_match = self.weather_city_re.match(query)
            city_name = city_match.group(1).strip() if city_match and city_match.group(1).strip() else "深圳"
            self.handle_weather(event, city_name)
        elif query == "讲个笑话":
            self.handle_joke(event)
        elif "今日油价" in query:
            self.handle_oil_price(event)
        elif query == "微博热搜":
            self.handle_weibo_hot(event)
        elif query == "名人名言":
            self.handle_famous_quotes(event)
        event.bypass()

    def handle_joke(self, event):
        url = "https://v2.alapi.cn/api/joke/random"
        payload = f"token={self.token}"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            joke_content = response.json()['data']['content']
            reply = Reply(ReplyType.TEXT, joke_content)
            event.channel.send(reply, event.message)
        else:
            logger.error(f"Failed to fetch joke: {response.text}")

    def handle_weather(self, event, city_name="深圳"):
        url = "https://v2.alapi.cn/api/tianqi/seven"
        payload = f"token={self.token}&city={city_name}"
        headers = {'Content-Type': "application/x-www-form-urlencoded; charset=utf-8"}
        response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)
        if response.status_code == 200:
            data = response.json()['data'][0]
            weather_info = (f"#{city_name}今日天气#\n"
                            f"白天天气：{data['wea_day']}，温度：{data['temp_day']}℃，风向：{data['wind_day']}，风力：{data['wind_day_level']}\n"
                            f"夜间天气：{data['wea_night']}，温度：{data['temp_night']}℃，风向：{data['wind_night']}，风力：{data['wind_night_level']}\n"
                            f"空气质量指数：{data['air']}({data['air_level']})\n"
                            f"日出：{data['sunrise']}，日落：{data['sunset']}\n"
                            f"降水量：{data['precipitation']}mm\n")
            for index in data['index']:
                weather_info += f"{index['name']}：{index['level']}\n"
            reply = Reply(ReplyType.TEXT, weather_info)
            event.channel.send(reply, event.message)
        else:
            logger.error(f"Failed to fetch weather: {response.text}")

    def handle_oil_price(self, event):
        url = "https://v2.alapi.cn/api/oil"
        payload = f"token={self.token}"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            oil_prices = "#各省份油价#\n\n"
            for item in data:
                oil_prices += (f"{item['province']} | 89号:{item['o89']} | 92号:{item['o92']} | "
                               f"95号:{item['o95']} | 98号:{item['o98']} | 0号柴油:{item['o0']}\n\n")
            reply = Reply(ReplyType.TEXT, oil_prices.strip())
            event.channel.send(reply, event.message)
        else:
            logger.error(f"Failed to fetch oil price: {response.text}")

    def handle_weibo_hot(self, event):
        url = "https://v2.alapi.cn/api/new/wbtop"
        payload = f"token={self.token}&num=10"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            hot_list = "#微博热搜榜#\n"
            for item in data:
                hot_list += f"{item['hot_word']} | {item['hot_word_num']}🔥\n"
            reply = Reply(ReplyType.TEXT, hot_list)
            event.channel.send(reply, event.message)
        else:
            logger.error(f"Failed to fetch weibo hot: {response.text}")

    def handle_famous_quotes(self, event):
        url = "https://v2.alapi.cn/api/mingyan"
        payload = f"token={self.token}&format=json"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            quote = f"{data['content']}\n\n—— {data['author']}"
            reply = Reply(ReplyType.TEXT, quote)
            event.channel.send(reply, event.message)
        else:
            logger.error(f"Failed to fetch famous quotes: {response.text}")

    def did_receive_message(self, event: Event):
        pass

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "此插件可以提供笑话、天气、油价、微博热搜和名人名言服务。"
