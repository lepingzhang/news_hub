# wechat-gptbot 资讯聚合获取插件

本项目作为 `wechat-gptbot` 插件，可以根据关键字回复对应的信息。

1. 早报可以配置定时推送给特定的私聊或群聊；
2. 手动获取早报回复消息为长图，定时推送则为文字；
3. “今天天气怎么样”默认城市是深圳，可修改默认城市；
4. 查询其他城市天气需要加上城市名，如“广州今天天气怎么样”

## 安装指南

### 1. 添加插件源
在 `plugins/source.json` 文件中添加以下配置：
```
{
  "keyword_reply": {
    "repo": "https://github.com/lepingzhang/news_hub.git",
    "desc": "获取聚合类资讯"
  }
}
```

### 2. 插件配置
在 `config.json` 文件中添加以下配置：
```
"plugins": [
  {
    "name": "news_hub",
    "schedule_time": "08:00",
    "single_chat_list": ["wxid_123"],
    "group_chat_list": ["123@chatroom"],
    "command": ["早报", "今天有什么新闻", "讲个笑话", "今天天气怎么样", "今日油价", "微博热搜", "名人名言"],
    "token": "your token"
  }
]
```

### 3. 获取早报API
在[这里](https://alapi.cn/api/view/93)获取`token`

## 感谢
参考了[plugin_weather](https://github.com/iuiaoin/plugin_weather)以及[plugin_dailynews](https://github.com/goxofy/plugin_dailynews)
