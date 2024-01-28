import requests
import schedule
import threading
import time
import re
from plugins import register, Plugin, Event, Reply, ReplyType, logger
from utils.api import send_txt

def send_img(image_url, target):
    # 实现发送图片的逻辑
    # 在这里添加发送图片的代码
    pass

@register
class NewsHub(Plugin):
    name = "news_hub"

    def __init__(self, config):
        super().__init__(config)
        self.scheduler_thread = None
        self.start_schedule()

    def will_generate_reply(self, event: Event):
        query = event.message.content.strip()
        is_group = event.message.is_group
        is_at = event.message.is_at

        # 如果是群聊并且艾特了机器人，尝试去除艾特部分
        if is_group and is_at:
            # 使用正则表达式去除艾特部分和后面的空白字符
            query = re.sub(r'@[\w]+\s+', '', query, count=1).strip()

        # 检查处理后的消息是否包含任一配置命令
        commands = self.config.get("command", [])
        if any(cmd in query for cmd in commands):
            if query in ["早报", "今天有什么新闻"]:
                self.handle_daily_news(event, reply_mode="image")
            elif "今天天气怎么样" in query:
                self.handle_weather(event, query.replace("今天天气怎么样", "").strip())
            elif query == "讲个笑话":
                self.handle_joke(event)
            elif "今日油价" in query:
                self.handle_oil_price(event)
            elif query == "微博热搜":
                self.handle_weibo_hot(event)
            elif query == "名人名言":
                self.handle_famous_quotes(event)
            event.bypass()
        else:
            # 如果消息内容不包含任一配置命令，可以记录日志或进行其他处理
            logger.info(f"Received a message but no command was found: {query}")

    def start_schedule(self):
        if self.scheduler_thread is None:
            schedule_time = self.config.get("schedule_time")
            if schedule_time:
                self.scheduler_thread = threading.Thread(target=self.run_schedule)
                self.scheduler_thread.start()
            else:
                logger.info("定时推送已取消")

    def run_schedule(self):
        schedule_time = self.config.get("schedule_time", "08:00")
        schedule.every().day.at(schedule_time).do(self.daily_push)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_daily_news(self, reply_mode="text"):
        token = self.config.get("token")
        zaobao_api_url = "https://v2.alapi.cn/api/zaobao"
        payload = f"token={token}&format=json"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}

        # 发送请求获取早报数据
        response = requests.request("POST", zaobao_api_url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            news_list = data['news']
            weiyu = data['weiyu']
            image_url = data['image']
            date = data['date']

            # 格式化文本消息
            formatted_news = f"【今日早报】{date}\n\n" + "\n".join(news_list) + f"\n\n{weiyu}"

            # 根据reply_mode返回不同类型的回复
            if reply_mode == "text":
                return formatted_news
            elif reply_mode == "image":
                return image_url
            elif reply_mode == "both":
                return [formatted_news, image_url]
        else:
            logger.error(f"Failed to fetch daily news: {response.text}")
            # 可以发送一条错误消息或者进行其他处理

    def daily_push(self):
        schedule_time = self.config.get("schedule_time")
        if not schedule_time:
            logger.info("定时推送已取消")
            return

        single_chat_list = self.config.get("single_chat_list", [])
        group_chat_list = self.config.get("group_chat_list", [])
        reply_content = self.get_daily_news(reply_mode="text")  # 以文本模式获取早报
        if reply_content:
            reply = Reply(ReplyType.TEXT, reply_content)  # 创建 Reply 对象
            self.push_to_chat(reply, single_chat_list, group_chat_list)

    def push_to_chat(self, reply, single_chat_list, group_chat_list):
        # 统一处理消息推送
        for chat_id in single_chat_list + group_chat_list:
            if reply.type == ReplyType.TEXT:
                send_txt(reply.content, chat_id)
            elif reply.type == ReplyType.IMAGE:
                send_img(reply.content, chat_id)

    def handle_daily_news(self, event, reply_mode="both"):
        token = self.config.get("token")
        zaobao_api_url = "https://v2.alapi.cn/api/zaobao"
        payload = f"token={token}&format=json"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}

        # 发送请求获取早报数据
        response = requests.request("POST", zaobao_api_url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            news_list = data['news']
            weiyu = data['weiyu']
            image_url = data['image']
            date = data['date']

            # 格式化文本消息
            formatted_news = f"【今日早报】{date}\n\n" + "\n".join(news_list) + f"\n\n{weiyu}"

            # 发送图片消息，如果是手动触发则只发送图片
            if image_url and (reply_mode == "image" or reply_mode == "both"):
                image_reply = Reply(ReplyType.IMAGE, image_url)
                event.channel.send(image_reply, event.message)
            
            # 发送文本消息，如果是定时推送则只发送文本
            if reply_mode == "text" or reply_mode == "both":
                text_reply = Reply(ReplyType.TEXT, formatted_news)
                event.channel.send(text_reply, event.message)
        else:
            logger.error(f"Failed to fetch daily news: {response.text}")
            # 可以发送一条错误消息或者进行其他处理

    def handle_joke(self, event):
        url = "https://v2.alapi.cn/api/joke/random"
        payload = f"token={self.config.get('token')}"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            joke_content = response.json()['data']['content']
            reply = Reply(ReplyType.TEXT, joke_content)
            event.channel.send(reply, event.message)
        else:
            logger.error(f"Failed to fetch joke: {response.text}")

    def handle_weather(self, event, query_city=None):
        # 如果用户提供了城市名称，则使用用户提供的；否则，默认使用深圳
        city_name = query_city if query_city else "深圳"
        url = "https://v2.alapi.cn/api/tianqi/seven"
        payload = f"token={self.config.get('token')}&city={city_name}"
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
        payload = f"token={self.config.get('token')}"
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
        payload = f"token={self.config.get('token')}&num=10"
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
        payload = f"token={self.config.get('token')}&format=json"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            quote = f"{data['content']}\n\n—— {data['author']}"
            reply = Reply(ReplyType.TEXT, quote)
            event.channel.send(reply, event.message)
        else:
            logger.error(f"Failed to fetch famous quotes: {response.text}")

    def help(self, **kwargs) -> str:
        return "每日定时或手动发送早报，及处理笑话、天气、油价、微博热搜和名人名言请求"

    def did_receive_message(self, event: Event):
        # 这里可以添加处理接收到的消息的逻辑
        # 如果没有特定的逻辑，可以简单地通过
        pass

    # 重写 will_decorate_reply 方法
    def will_decorate_reply(self, event: Event):
        # 这里可以添加在发送回复之前的装饰逻辑
        # 如果没有特定的逻辑，可以简单地通过
        pass

    # 重写 will_send_reply 方法
    def will_send_reply(self, event: Event):
        # 这里可以添加发送回复之前的逻辑
        # 如果没有特定的逻辑，可以简单地通过
        pass
