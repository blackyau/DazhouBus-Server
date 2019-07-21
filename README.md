# DazhouBus-Server

达州实时公交 微信小程序 服务端,客户端请看 [这里](https://github.com/blackyau/DazhouBus-Client)

## 获取最新主页数据

下载源码后直接运行 GetIndexData.py

```shell
python GetIndexData.py
```

信息就会打印在控制台，直接复制粘贴到 [DazhouBus-Client/pages/index/index.js#L7](https://github.com/blackyau/DazhouBus-Client/blob/master/pages/index/index.js#L7) 即可。这里手动排序了以下，把K线全都置顶了，其他线路就由从小到大的顺序排列。

## 搭建服务端

### 依赖安装

Python 3

```shell
pip install flask flask_restful requests gunicorn
```

### 运行

> SSL证书推荐使用 [acme.sh](https://github.com/Neilpang/acme.sh) 强烈推荐使用 [DNS API](https://github.com/Neilpang/acme.sh/wiki/dnsapi)

```shell
gunicorn --certfile=server.crt --keyfile=server.key --bind 127.0.0.1:443 wsgi:app
```

终端打印出类似以下信息说明运行成功

```shell
[2019-07-21 15:33:25 +0800] [21699] [INFO] Starting gunicorn 19.9.0
[2019-07-21 15:33:25 +0800] [21699] [INFO] Listening at: https://127.0.0.1:443 (21699)
[2019-07-21 15:33:25 +0800] [21699] [INFO] Using worker: sync
[2019-07-21 15:33:25 +0800] [21702] [INFO] Booting worker with pid: 21702
```

Linux 下你需要使用类似 `screen` 之类的命令让它保持在后台运行

#### Nginx

如果你使用一台单独的 WEB 服务器来提供服务，以上就是最简的部署方法。如果你现在正在使用 Nginx ，那么你可以参考以下配置文件通过 Nginx 代理将请求转发到 flask 。

```conf
server {
    listen       443 ssl http2;
    server_name  api.example.com;
    server_tokens        off;

    #access_log  /tmp/api.log;

    ssl_certificate     /etc/nginx/ssl/example.com.ecc.crt;
    ssl_certificate_key /etc/nginx/ssl/example.com.ecc.key;

    # openssl dhparam -out dhparams.pem 2048
    # https://weakdh.org/sysadmin.html
    ssl_dhparam         /etc/nginx/ssl/dhparam.pem;

    ssl_ciphers                EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;

    ssl_prefer_server_ciphers  on;

    ssl_protocols              TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_session_cache          shared:SSL:50m;
    ssl_session_timeout        1d;

    location / {
        root   /etc/nginx/html;
        index  index.html;
    }

    location /bus {
        proxy_pass http://127.0.0.1:8866;
        proxy_redirect     off;
        proxy_set_header   Host                 $http_host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }

}

server {
    server_name  api.example.com;
    server_tokens     off;

    #access_log  logs/host.access.log;

    if ($request_method !~ ^(GET|HEAD|POST)$ ) {
        return        444;
    }

    location / {
        rewrite       ^/(.*)$ https://api.example.com/$1 permanent;
    }
}
```

## API分析

[Postman documenter - 中电信用 公交API](https://documenter.getpostman.com/view/4968764/SVSNKSwr)

### 查询公交信息

POST http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getlineandstartendinfo

```shell
curl --location --request POST "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getlineandstartendinfo" \
  --header "User-Agent: okhttp/3.9.0" \
  --header "Content-Type: application/json" \
  --header "Accept-Encoding: gzip" \
  --data "{
    \"lineNo\": \"11\",
    \"isUpDown\": \"0\",
    \"cityCode\": \"6750\"
}"
```

| Key | Value | Description |
| --- | --- | --- |
| lineNo | 11 | 要查询的线路名，可以带中文。例如:11路 |
| isUpDown | 0 | 线路上下行状态，可取0或1 |
| cityCode | 6750 | 城市代码,目前已知可取 达州市6750 保定1340 |

返回示例:

```json
{
	"jsonResult":[
		{
			"cityCode":6750,
			"firstTime":"04:30:00",
			"isUpDown":0,
			"lastTime":"21:15:00",
			"lineName":"11路",
			"lineNo":"111",
			"lineUpDownNo":"",
			"stationFirst":"火车站公交枢纽站",
			"stationLast":"徐家坝公交首末站"
		},
		{
			"cityCode":6750,
			"firstTime":"04:30:00",
			"isUpDown":1,
			"lastTime":"21:20:00",
			"lineName":"11路",
			"lineNo":"111",
			"lineUpDownNo":"",
			"stationFirst":"徐家坝公交首末站",
			"stationLast":"火车站公交枢纽站"
		}
	],
	"message":"ok",
	"status":"200"
}
```

### 查询线路信息

POST http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getonelineandstartendinfo

```shell
curl --location --request POST "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getrunningbusesbyline" \
  --header "Content-Type: application/json" \
  --header "User-Agent: okhttp/3.9.0" \
  --header "Accept-Encoding: gzip" \
  --data "{
	\"lineNo\":\"111\",
	\"isUpDown\":\"0\",
	\"cityCode\":\"6750\"
}"
```

| Key | Value | Description |
| --- | --- | --- |
| lineNo | 111 | 要查询的线路唯一标识,需要从上一个API获得 |
| isUpDown | 0 | 线路上下行状态，可取0或1 |
| cityCode | 6750 | 城市代码,目前已知可取 达州市6750 保定1340 |

返回示例:

```json
{
	"jsonResult": {
		"linestations": [
			{
				"cityCode": 6750,
				"isUpDown": 0,
				"labelNo": 1,
				"lineNo": "1001",
				"stationId": "1320",
				"stationName": "火车站公交枢纽站"
			},
			/*过长中间省略*/
			{
				"cityCode": 6750,
				"isUpDown": 0,
				"labelNo": 9,
				"lineNo": "1001",
				"stationId": "1328",
				"stationName": "徐家坝公交首末站"
			}
		],
		"lineInfo": {
			"cityCode": 6750,
			"firstTime": "06:20:00",
			"isUpDown": 0,
			"lastTime": "20:15:00",
			"lineName": "K1路",
			"lineNo": "1001",
			"lineUpDownNo": "",
			"stationFirst": "火车站公交枢纽站",
			"stationLast": "徐家坝公交首末站"
		}
	},
	"message": "ok",
	"status": "200"
}
```

### 查询车辆运行状态

POST http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getrunningbusesbyline

```shell
curl --location --request POST "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getonelineandstartendinfo" \
  --header "Content-Type: application/json" \
  --header "User-Agent: okhttp/3.9.0" \
  --header "Accept-Encoding: gzip" \
  --data "{
	\"lineNo\":\"111\",
	\"isUpDown\":\"0\",
	\"cityCode\":\"6750\"
}"
```

| Key | Value | Description |
| --- | --- | --- |
| lineNo | 111 | 要查询的线路唯一标识,需要从第一个API获得 |
| isUpDown | 0 | 线路上下行状态，可取0或1 |
| cityCode | 6750 | 城市代码,目前已知可取 达州市6750 保定1340 |

返回示例:

```json
{
	"jsonResult": [
		{
			"busNo": "1133",
			"cityCode": 6750,
			"isUpDown": 0,
			"labelNo": 1,
			"lineNo": "111"
		},
        /*省略*/
		{
			"busNo": "1132",
			"cityCode": 6750,
			"isUpDown": 0,
			"labelNo": 6,
			"lineNo": "111"
		},
		{
			"busNo": "1103",
			"cityCode": 6750,
			"isUpDown": 0,
			"labelNo": 9,
			"lineNo": "111"
		}
	],
	"message": "ok",
	"status": "200"
}
```
