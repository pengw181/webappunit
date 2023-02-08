# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/20 上午11:22

import json
import flask
from datetime import datetime
from werkzeug.routing import BaseConverter
from src.main.python.core.gooflow.case import loadCase
from src.main.python.conf.loads import properties

app = flask.Flask(__name__)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter


@app.route('/http/web-test', methods=['GET', 'POST'])
def main():
    print("------------------------")

    req_method = flask.request.method
    print("req_method: {}".format(req_method))
    print("req_form: {}".format(flask.request.form.to_dict()))

    # runAllTest为true时，runTestLevel不生效；runAllTest为false时，只执行runTestLevel指定级别的用例
    properties["runAllTest"] = True
    # 用例执行失败，是否继续执行下一条
    properties["continueRunWhenError"] = False
    # 设置测试用例覆盖级别
    properties["runTestLevel"] = ["高", "中", "低"]
    # 是否输出报告
    properties["builtReport"] = False

    # 开始运行，第一个数字为读取第几个测试用例文件（从1开始），第二个数字为读取测试用例的第几行（从1开始）
    begin_file = int(flask.request.form.get("begin_file"))
    begin_case = int(flask.request.form.get("begin_case"))
    print(begin_file)
    print(begin_case)
    loadCase(begin_file, begin_case)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8099, debug=True)
