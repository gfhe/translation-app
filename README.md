# 环境安装

```shell
pip install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
```


# 环境变量说明

DEVICE可配置cpu/cuda
端口7000

# gunicorn 说明
gunicorn 命令行执行时，如`gunicorn -c gunicorn_config.py translation:apps`,
指定的`translation:apps`中，
* translation表示启动python文件为`translation.py`; 
* `apps`表示translation.py中声明的Flask对象名。