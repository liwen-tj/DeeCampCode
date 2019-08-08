import os
import pandas as pd
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import json
import csv
from model.predict.yuce import yuce
from utils.csv2pdf import csv2pdf

app = Flask(__name__)
CORS(app)


@app.route('/fake_upload', methods=['POST'])
def fake_predict():
    file = request.files['file']
    return jsonify("fake")

@app.route('/predict', methods=['POST'])
def hospital_setting():
    file = request.files['file']
    raw_data = pd.read_csv(file, index_col=0)
    result_data = yuce(raw_data).reset_index()
    result_data = result_data.loc[:, ["就诊号","性别","年龄（天）","当前科室","手术名称","医生","手术时长(分钟)","麻醉方式","手术级别"]]
    result_data.columns = ["id","gender","age","department","operatingName","doctorName","predTime","anaesthetic","rank"]
    result_data.insert(1, "name", result_data["doctorName"])
    result_data["key"] = range(len(result_data))
    result_data["orId"] = ""
    result_data["startTime"] = ""
    result_data["age"] = (result_data["age"] / 365).astype(int)
    result_data["predTime"] = result_data["predTime"].astype(int)
    key = result_data.key
    result_data = result_data.drop("key", axis=1)
    result_data.insert(0, "key", key)
    # print(result_data.to_json(orient="records",force_ascii=False))
    return result_data.to_json(orient="records",force_ascii=False)

@app.route('/schedule', methods=['POST'])
def table():
    input_overall = request.get_json()
    input_length = len(input_overall)
    # 患者信息
    input_json = input_overall[0:input_length - 1]
    # 环境变量
    input_config = input_overall[-1]

    output_json, output_overall = fakeSchefule(input_json, input_config)
    print(output_json, output_overall)
    output_json.append(output_overall)
    print(output_json)

    return jsonify(output_json)

def fakeSchefule(input_json, input_config):
    output_json = [
        {
            "key": "0",
            "id": "1",
            "name": "尹小帆",
            "gender": "男",
            "age": "70",
            "department": "心血管科",
            "operatingName": "心脏搭桥手术",
            "doctorName": "李四",
            "predTime": "120",
            "anaesthetic": "全身麻醉",
            "rank": "2",
            "orId": "10",
            "startTime": "8:00",
            "recoverDuration": 15,
            "cleanDuration": 20,
        }, {
            "key": "1",
            "id": "2",
            "name": "司徒",
            "gender": "女",
            "age": "23",
            "department": "妇产科",
            "operatingName": "剖腹产手术",
            "doctorName": "王小二",
            "predTime": "100",
            "anaesthetic": "局部麻醉",
            "rank": "1",
            "orId": "7",
            "startTime": "9:00",
            "recoverDuration": 15,
            "cleanDuration": 20,
        }
    ]
    output_overall = {
        "orRatio": "0.99999",
        "recoverRoomRatio": "0.8",
        "extraHours": [4, 5, 6],
        "extraHourRatio": [0.4, 0.2, 0.9],
    }

    return output_json, output_overall

@app.route('/preview', methods=['POST'])
def preview_pdf():
    data = json.loads(request.data)

    csv_file = './data/preview.csv'
    with open(csv_file, 'w') as csvfile:
        fieldnames = ['orId', 'startTime', 'predTime', 'id', 'name',
                      'gender', 'age', 'operatingName', 'department', 
                      'doctorName', 'anaesthetic', 'recoverDuration', 'cleanDuration', 'key', 'rank']
        headername = {
            'orId': '手术室',
            'startTime': '开始时间', 
            'predTime': '预测时长(分钟)', 
            'id': '住院号', 
            'name': '姓名',
            'gender': '性别', 
            'age': '年龄', 
            'operatingName': '手术名称', 
            'department': '科室',
            'doctorName': '医生', 
            'anaesthetic': '麻醉方式', 
            'recoverDuration': '恢复时间',  
            'cleanDuration': '清洁时间',
            'key': 'key',
            'rank': 'rank'
        }
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(headername)
        writer.writerows(data)
    
    csv2pdf(csv_file)
    return send_from_directory('./data/', 'preview.pdf', as_attachment=True)


if __name__ == '__main__':
    app.run()
