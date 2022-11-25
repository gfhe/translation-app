# 多语种翻译服务
模型：
* `facebook/m2m100_418M`
* `facebook/mbart-large-50-many-to-many-mmt`


## 使用

* 服务端口: 7000
* HTTP method: POST
* 参数：
  * `text`: 待翻译的文本内容
  * `src`: 源语种
  * `dest`:语种目标

请求例子：
```
curl  -v  -X POST  "http://localhost:7000/translate" -d '{"dest": "Chinese","src": "English","text": "I love China"}'
```

### 源码安装
环境配置：
```shell
pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
```

运行：
```shell
gunicorn -c gunicorn_config.py translation:apps
```


