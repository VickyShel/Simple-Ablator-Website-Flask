# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import math
import shutil

# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask
from flask import make_response
from flask import request
from flask import jsonify
import requests
import zipfile
import os
import json
from flask_cors import CORS

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("hhh")
    print(request.files)
    print(request.files['zipFile'])
    result=[]
    names=[]
    current_path = os.path.abspath(__file__)
    path=os.path.dirname(current_path)
    if 'zipFile' in request.files:
        print("/////")
        zip_file = request.files['zipFile']

        # 保存 zip 压缩包到临时目录
        zip_file.save(path +'/'+ zip_file.filename)
        shutil.rmtree(path+'/unzipped_files')
        with zipfile.ZipFile(path+zip_file.filename, 'r') as zip_ref:
            print("read file success")
            # 解压缩文件到指定目录
            zip_ref.extractall(path+'/unzipped_files')
        result_file_paths=find_result_json_files(path+'/unzipped_files')
        print(result_file_paths)
        flags=[]
        for file_path in result_file_paths:
            paths=file_path.split('/')
            names.append(paths[-2])
            result_json={}
            with open(file_path, 'r') as file:
                data_list =  file.read().split("}\n{")

                # 解析每个JSON对象
                for json_str in data_list:
                    # print(json_str)
                    # print(json_str[-1])
                    # print(json_str[0])
                    if json_str[-1]!='}' and json_str[-2]!='}':
                        # print("add }")
                        json_str=json_str+'}'
                    if json_str[0]!='{':
                        json_str='{'+json_str
                        # print("add {")
                    # print(json_str)
                    data = json.loads(json_str)
                    for key in data:
                        # print(type(data[key]))
                        if key in result_json:
                            result_json[key].append(data[key])
                        else:
                            result_json[key]=[data[key]]
                        if math.isinf(data[key]) or math.isnan(data[key]):
                            if key not in flags:
                                flags.append(key)

            print(result_json)
            result.append(result_json)
        print(flags)
        for item in result:
            for key in flags:
                item.pop(key)
        print(result)
        results=[]
        results.append(result)
        results.append(names)
        return jsonify(results)

        # return 'Zip file uploaded successfully'
    # return 'No zip file uploaded'

def find_result_json_files(folder_path):
    # print(folder_path)
    result_json_files = []

    # 遍历当前文件夹中的所有文件和文件夹
    for entry in os.listdir(folder_path):
        entry_path = os.path.join(folder_path, entry)

        # 如果是文件夹，则递归调用函数继续遍历子文件夹
        if os.path.isdir(entry_path) and entry!='__MACOSX':
            result_json_files.extend(find_result_json_files(entry_path))

        # 如果是文件，并且文件名是 'result.json'，则将其加入结果列表中
        elif os.path.isfile(entry_path) and entry == 'results.json':
            result_json_files.append(entry_path)
    print(result_json_files)

    return result_json_files

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=5500, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
