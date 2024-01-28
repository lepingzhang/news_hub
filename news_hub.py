import requests
from plugins import register, Plugin, Event, logger

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

    def will_generate_reply(self, event: Event):
        query = event.message.content.strip()
        commands = self.config.get("command", [])
        if query in commands or any(query.startswith(cmd) for cmd in commands):
            if query == "讲个笑话":
                self.handle_joke(event)
            elif query.startswith("今天天气怎么样"):
                city_name = query.replace("今天天气怎么样", "").strip() or "深圳"
                self.handle_weather(event, city_name)
            elif query.startswith("今日油价"):
                province_name = query.replace("今日油价", "").strip() or None
                self.handle_oil_price(event, province_name)
            elif query == "微博热搜":
                self.handle_weibo_hot(event)
            elif query == "名人名言":
                self.handle_famous_quotes(event)
            event.bypass()

    # Handlers for different APIs
    def handle_joke(self, event):
        url = "https://v2.alapi.cn/api/joke/random"
        payload = f"token={self.token}"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            joke_content = data['content']
            event.channel.send(joke_content, event.message)

    def handle_weather(self, event, city_name="深圳"):
        url = "https://v2.alapi.cn/api/tianqi/seven"
        payload = f"token={self.token}&city={city_name}"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data'][0]  # 取得第一天的数据
            weather_info = f"{data['city']}的天气：{data['wea_day']}，{data['temp_day']} - {data['temp_night']}，风向：{data['wind_day']} {data['wind_day_level']}"
            event.channel.send(weather_info, event.message)

    def handle_oil_price(self, event, province_name=None):
        url = "https://v2.alapi.cn/api/oil"
        payload = f"token={self.token}"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            if province_name:
                price_info = next((item for item in data if item['province'] == province_name), None)
                if price_info:
                    event.channel.send(f"{province_name}油价：89号-{price_info['o89']}，92号-{price_info['o92']}，95号-{price_info['o95']}，98号-{price_info['o98']}，0号柴油-{price_info['o0']}", event.message)
            else:
                for item in data:
                    event.channel.send(f"{item['province']}油价：89号-{item['o89']}，92号-{item['o92']}，95号-{item['o95']}，98号-{item['o98']}，0号柴油-{item['o0']}", event.message)

    def handle_weibo_hot(self, event):
        url = "https://v2.alapi.cn/api/new/wbtop"
        payload = f"token={self.token}&num=10"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            hot_words = "\n".join([f"{item['hot_word']}：{item['hot_word_num']}" for item in data])
            event.channel.send(hot_words, event.message)

    def handle_famous_quotes(self, event):
        url = "https://v2.alapi.cn/api/mingyan"
        payload = f"token={self.token}&format=json"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            quote_content = f"{data['content']} —— {data['author']}"
            event.channel.send(quote_content, event.message)

    def did_receive_message(self, event: Event):
        # 处理接收到的消息，如果需要的话
        pass

    def will_decorate_reply(self, event: Event):
        # 在发送回复之前进行装饰，如果需要的话
        pass

    def will_send_reply(self, event: Event):
        # 在发送回复之前的最后一步，如果需要的话
        pass

    def help(self, **kwargs) -> str:
        # 返回插件的帮助信息
        return "此插件可以提供笑话、天气、油价、微博热搜和名人名言服务。"
