# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/20 上午11:22

import sys
from src.main.python.core.gooflow.case import loadCase
from src.main.python.conf.loads import properties


def main(begin_file_line, begin_case_line):

    # runAllTest为true时，runTestLevel不生效；runAllTest为false时，只执行runTestLevel指定级别的用例
    properties["runAllTest"] = True
    # 用例执行失败，是否继续执行下一条
    properties["continueRunWhenError"] = False
    # 设置测试用例覆盖级别
    properties["runTestLevel"] = ["高", "中", "低"]
    # 是否输出报告
    properties["builtReport"] = False

    # 开始运行，第一个数字为读取第几个测试用例文件（从1开始），第二个数字为读取测试用例的第几行（从1开始）
    loadCase(begin_file_line, begin_case_line)


if __name__ == "__main__":
    print("自动化测试启动，开始接收参数")
    begin_file = sys.argv[1]
    begin_case = sys.argv[2]
    print("接收参数: {}, {}".format(begin_file, begin_case))
    main(begin_file, begin_case)

