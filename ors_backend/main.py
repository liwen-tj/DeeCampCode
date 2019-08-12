import os
import pandas as pd
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import json
import csv
from model.predict.yuce import yuce
from model.predict.yuce import yujiazai
from utils.csv2pdf import csv2pdf
from model.schedule.save.MultiScheduler import Scheduler
from model.predict.jie import jieshi
from model.predict.xunlian import xunlian
from faker import Faker
f=Faker(locale='zh_CN')

app = Flask(__name__)
CORS(app)


@app.route('/fake_upload', methods=['POST'])
def fake_predict():
    file = request.files['file']
    raw_data = pd.read_csv(file, index_col=0)
    print(xunlian(raw_data))
    return jsonify("已建立模型")

@app.route('/predict', methods=['POST'])
def hospital_setting():
    file = request.files['file']
    raw_data = pd.read_csv(file, index_col=0)
    jieshi_data = jieshi(raw_data)
    result_data = yuce(raw_data, modely).reset_index()
    result_data = result_data.loc[:, ["就诊号","性别","年龄（天）","当前科室","手术名称","医生","手术时长(分钟)","麻醉方式","手术级别"]]
    result_data.columns = ["id","gender","age","department","operatingName","doctorName","predTime","anaesthetic","rank"]
    result_data.insert(1, "name", result_data["doctorName"])
    for i in range(len(result_data)):
        result_data["name"][i] = f.name()
    result_data["key"] = range(len(result_data))
    result_data["orId"] = ""
    result_data["startTime"] = ""
    result_data["age"] = (result_data["age"] / 365).astype(int)
    result_data["predTime"] = result_data["predTime"].astype(int)
    key = result_data.key
    result_data = result_data.drop("key", axis=1)
    result_data.insert(0, "key", key)
    data = {}
    data["predict"] = result_data.to_json(orient="records", force_ascii=False)
    data["jieshi"] = jieshi_data
    # print(result_data.to_json(orient="records",force_ascii=False))
    # return data.to_json(orient="records", force_ascii=False)
    return json.dumps(data, ensure_ascii=False)


@app.route('/schedule', methods=['POST'])
def table():
    print("schedule executing...")
    input_overall = request.get_json()
    input_length = len(input_overall)
    # 患者信息
    input_json = input_overall[0:input_length - 1]
    # 环境变量
    input_config = input_overall[-1]

    input_config['start_time'] = input_config['start_time'][11:16]
    input_config['start_time'] = list(input_config['start_time'])
    input_config['start_time'][1] = str((int(input_config['start_time'][1]) + 8) % 24)
    input_config['start_time'] = ''.join(input_config['start_time'])
    input_config['end_time'] = input_config['end_time'][11:16]
    input_config['end_time'] = list(input_config['end_time'])
    input_config['end_time'][1] = str((int(input_config['end_time'][1]) + 8) % 24 )

    input_config['end_time'] = ''.join(input_config['end_time'])
    # print(input_config)

    output_json, output_overall = Scheduler(input_json, input_config)
    print(output_json)
    # print(output_json, output_overall)
    output_json = json.loads(output_json)
    output_json.append(output_overall)
    # print(output_json)
    print("schedule done")
    return jsonify(output_json)

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
    modely = yujiazai()
    app.run()



