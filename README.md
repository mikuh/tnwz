# tnwz
头脑王者辅助工具

暂时是手动版的，自动化现在懒得写。改天有兴致了补上。


## 使用说明：

这里以windows为例，linux大同小异。

安装mitmproxy：

```
pip install mitmproxy
```

执行listen.py：

```
mitmdump -p 8123 -s listen.py
```

手机连接到和电脑同一个wifi，设置代理内网ip+端口8123，然后手机浏览器访问`mitm.it`

下载并安装证书，ios需要设置信任(【设置】>【通用】>【关于本机】>【证书信任设置】)

然后就可以开始玩了。 正确的答案标识为`【True】`