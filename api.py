# coding:utf-8
from flask import Flask
from flask_restful import Resource, Api, request
import requests
import json

headers = {
        'User-Agent': 'okhttp/3.9.0',
        'Accept-Encoding': 'gzip'
}


# 查询线路
def get_lines(line_no, up_or_down=1, city_code=6750):
    url = "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getlineandstartendinfo"
    data = json.dumps({'lineNo': line_no, 'isUpDown': up_or_down, 'cityCode': city_code})
    r = requests.post(url, headers=headers, data=data)
    if r.json()["status"] == "200":
        return r
    else:
        raise Warning("返回数据异常!以下是 API 返回信息\n" + r.text)


# 获取线路信息(停靠站点)
def get_line_info(line_no, up_or_down=1, city_code=6750):
    url = "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getonelineandstartendinfo"
    data = json.dumps({'lineNo': line_no, 'isUpDown': up_or_down, 'cityCode': city_code})
    r = requests.post(url, headers=headers, data=data)
    if r.json()["status"] == "200":
        return r
    else:
        raise Warning("返回数据异常!以下是 API 返回信息\n" + r.text)


# 获取运行状态
def get_running_info(line_no, up_or_down, city_code=6750):
    url = "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getrunningbusesbyline"
    data = json.dumps({'lineNo': line_no, 'isUpDown': up_or_down, 'cityCode': city_code})
    r = requests.post(url, headers=headers, data=data)
    if r.json()["status"] == "200":
        return r
    else:
        raise Warning("返回数据异常!以下是 API 返回信息\n" + r.text)


app = Flask(__name__)
api = Api(app)


class Findlineinfo(Resource):
    def post(self):
        data = request.get_json()
        if data is None:
            return {"status": 400}
        try:
            out = get_lines(data['lineNo'], data['isUpDown'], data['cityCode'])
            return out.json()
        except Warning:
            return 500


class Getlineinfo(Resource):
    def post(self):
        data = request.get_json()
        if data is None:
            return {"status": 400}
        try:
            out = get_line_info(data['lineNo'], data['isUpDown'], data['cityCode'])
            return out.json()
        except Warning:
            return 500


class Runninginfo(Resource):
    def post(self):
        data = request.get_json()
        if data is None:
            return {"status": 400}
        try:
            out = get_running_info(data['lineNo'], data['isUpDown'], data['cityCode'])
            return out.json()
        except Warning:
            return 500


api.add_resource(Findlineinfo, '/bus/findlineinfo')
api.add_resource(Getlineinfo, '/bus/getlineinfo')
api.add_resource(Runninginfo, '/bus/runninginfo')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8866)
