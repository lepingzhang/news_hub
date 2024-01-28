# wechat-gptbot 资讯聚合获取插件

本项目作为 `wechat-gptbot` 插件，可以根据关键字回复对应的信息。

## 安装指南

### 1. 添加插件源
在 `plugins/source.json` 文件中添加以下配置：
```
{
  "keyword_reply": {
    "repo": "https://github.com/lepingzhang/news_hub.git",
    "desc": "每日早报"
  }
}
```

### 2. 插件配置
在 `config.json` 文件中添加以下配置：
```
"plugins": [
  {
    "name": "news_hub",
    "command": ["讲个笑话", "今天天气怎么样", "今日油价", "微博热搜", "名人名言"],
    "token": "your_token_here"
  }
]
```

### 3. 获取早报API
在[这里](https://alapi.cn/api/view/93)获取`token`

## 感谢
参考了[plugin_weather](https://github.com/iuiaoin/plugin_weather)以及[plugin_dailynews](https://github.com/goxofy/plugin_dailynews)
