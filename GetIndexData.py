import requests
import json

headers = {
    'User-Agent': 'okhttp/3.9.0',
    'Accept-Encoding': 'gzip'
}


def get_lines(line_no, up_or_down=1, city_code=6750):
    url = "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getlineandstartendinfo"
    data = json.dumps({'lineNo': line_no, 'isUpDown': up_or_down, 'cityCode': city_code})
    r = requests.post(url, headers=headers, data=data)
    if r.json()["status"] == "200":
        return r
    else:
        raise Warning("返回数据异常!以下是 API 返回信息\n" + r.text)


def get_line_info(line_no, up_or_down=1, city_code=6750):
    url = "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getonelineandstartendinfo"
    data = json.dumps({'lineNo': line_no, 'isUpDown': up_or_down, 'cityCode': city_code})
    r = requests.post(url, headers=headers, data=data)
    if r.json()["status"] == "200":
        return r
    else:
        raise Warning("返回数据异常!以下是 API 返回信息\n" + r.text)


def get_running_info(line_no, up_or_down, city_code=6750):
    url = "http://ssgj.cecurs.com:32020/nextbusservice/stationlineinfo/getrunningbusesbyline"
    data = json.dumps({'lineNo': line_no, 'isUpDown': up_or_down, 'cityCode': city_code})
    r = requests.post(url, headers=headers, data=data)
    if r.json()["status"] == "200":
        return r
    else:
        raise Warning("返回数据异常!以下是 API 返回信息\n" + r.text)


line_info_list = []
lineNo_list = []
for i in range(1, 10):
    lines_info = get_lines(i).json()["jsonResult"]
    for one_info in lines_info:
        if one_info['isUpDown'] == 1:
            continue
        if int(one_info['lineNo']) in lineNo_list:
            continue
        lineNo_list.append(int(one_info['lineNo']))
        line_info_list.append({'lineNo': one_info['lineNo'], 'lineName': one_info['lineName'],
                               'isUpDown': one_info['isUpDown'], 'stationFirst': one_info['stationFirst'],
                               'stationLast': one_info['stationLast']})
lineNo_list.sort()
lineNo_final = []
for line_num in lineNo_list:
    if line_num > 999:
        lineNo_final.append(line_num)
lineNo_final.extend(lineNo_list[:len(lineNo_list) - len(lineNo_final)])

line_info_out = []
for i in lineNo_final:
    for one_info in line_info_list:
        if i == int(one_info['lineNo']):
            line_info_out.append(one_info)
            continue
print('总数据量:', len(line_info_out))
print(line_info_out)
