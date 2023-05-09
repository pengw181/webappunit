# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/20 上午10:32

import xlrd
import xlwt
import json
import traceback
import requests
from xlutils.copy import copy
from datetime import datetime
from time import sleep
from src.main.python.lib.logger import log
from src.main.python.lib.globals import gbl
from src.main.python.lib.generateUUID import getUUID
from src.main.python.core.gooflow.report import ReportRunner
from src.main.python.core.gooflow.precondition import preconditions
from src.main.python.core.gooflow.operation import basic_run
from src.main.python.core.gooflow.compares import compare_data
from src.main.python.core.gooflow.initiation import Initiation, initiation_work
# from src.main.python.lib.thds import stop_thread


def loadCase(filenum, rownum, callback_url=None):

    # 开始测试前，数据初始化
    initiation_work()

    # 生成文件夹uuid，用于保存截图
    gbl.service.set("FolderID", getUUID())

    # 定义报表输出对象
    report_info = []

    # 根据当前测试应用名，打开相应的测试用例集
    application = gbl.service.get("application")
    if application is None:
        raise Exception("!!! application未设置.")
    path = gbl.service.get("ControllerPath") + application + "/controller.xls"
    log.info("打开{0},开始获取测试用例文件名".format(path))
    # 打开excel，formatting_info=True保留Excel当前格式
    rbook = xlrd.open_workbook(path, formatting_info=True)

    wbook = copy(rbook)

    rsheets = rbook.sheet_by_name('Sheet1')
    wsheets = wbook.get_sheet(0)
    nrows = rsheets.nrows

    row_num = filenum
    str1 = rsheets.cell(row_num, 0).value
    str2 = rsheets.cell(row_num, 1).value

    while len(str1) > 0:

        # 定义字体类型1. 字体：红色
        font0 = xlwt.Font()
        font0.colour_index = 2
        font0.bold = True

        style0 = xlwt.XFStyle()
        style0.font = font0

        # 定义字体类型2. 字体：蓝色
        font1 = xlwt.Font()
        font1.colour_index = 4
        font1.bold = True

        style1 = xlwt.XFStyle()
        style1.font = font1

        # 定义字体类型3. 字体：绿色
        font2 = xlwt.Font()
        font2.colour_index = 3
        font2.bold = True

        style2 = xlwt.XFStyle()
        style2.font = font2

        if not str2 or str2 == "否":
            log.info("用例文件{0}已设置不执行，跳过.".format(str1))
            wsheets.write(row_num, 2, "NO TEST", style1)
            wsheets.write(row_num, 3, "")
            wsheets.write(row_num, 4, "")
            row_num += 1
            if row_num < nrows:
                str1 = rsheets.cell(row_num, 0).value
                str2 = rsheets.cell(row_num, 1).value
            else:
                break
        else:
            str1 = rsheets.cell(row_num, 0).value
            start_time = datetime.now().strftime('%Y%m%d%H%M%S')
            wsheets.write(row_num, 2, "RUNNING", style2)
            wsheets.write(row_num, 3, start_time)
            wsheets.write(row_num, 4, "")
            wbook.save(path)

            filename = gbl.service.get("TestCasePath") + application + "/" + str1
            log.info("获取到测试用例文件：{0}".format(filename))
            case = CaseWorker(case_path=filename)
            result = case.worker(row_num=rownum)
            report_info.append(case.run_info)

            if result:
                style = style1
                status = "PASS"
            else:
                style = style0
                status = "FAIL"
            end_time = datetime.now().strftime('%Y%m%d%H%M%S')
            wsheets.write(row_num, 2, status, style)
            wsheets.write(row_num, 4, end_time)
            wbook.save(path)
            if not result:
                if gbl.service.get("ContinueRunWhenError"):
                    rownum = 1
                    row_num += 1
                    if row_num == nrows:
                        break
                    else:
                        sleep(3)
                        str1 = rsheets.cell(row_num, 0).value
                        str2 = rsheets.cell(row_num, 1).value
                else:
                    break
            else:
                rownum = 1
                row_num += 1
                if row_num == nrows:
                    break
                else:
                    sleep(3)
                    str1 = rsheets.cell(row_num, 0).value
                    str2 = rsheets.cell(row_num, 1).value

    if gbl.service.get("BuiltReport"):
        log.info("开始生成测试报告...")
        report = ReportRunner()
        report_save_path = report.generateReportFile(report_info)
        log.info("测试报告生成成功，报告存放路径: {0}\n".format(report_save_path))
    log.info("----------------------本测试执行完成----------------------")
    log.info(report_info)
    gbl.service.set("TestResult", report_info)
    # 测试完成后，关闭浏览器，关闭线程
    # stop_thread(gbl.service.get("Thread"))
    # gbl.service.get("browser").quit()

    # 回调返回测试结果
    # url = "http://192.168.31.64:8098/http/web-test/result"
    url = callback_url
    data = {
        "success": True,
        "result": report_info
    }
    headers = {
        "Content-Type": "application/json"
    }
    log.info("测试结束，返回测试结果数据: {}".format(data))
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False, timeout=60)
    log.info(response.json())


class CaseWorker:

    def __init__(self, case_path, sheet_index=0):

        self.path = case_path
        self.successNum = 0
        self.failNum = 0
        self.skipNum = 0
        self.to_end = False
        self.run_info = {}
        self.case_file_result = {}

        # 打开excel，formatting_info=True保留Excel当前格式
        self.rbook = xlrd.open_workbook(self.path, formatting_info=True)

        self.wbook = copy(self.rbook)

        self.rsheets = self.rbook.sheet_by_index(sheet_index)
        self.wsheets = self.wbook.get_sheet(0)

        self.nrows = self.rsheets.nrows
        self.ncols = self.rsheets.ncols
        log.info("Excel行数：{0}, 列数 : {1}".format(self.nrows, self.ncols))
        log.info('-------------------------------------------------------------------------')

    def column_definition(self, row_num):

        column = []
        # 用例名称
        case_name = self.rsheets.cell(row_num, 0).value
        column.append(case_name)

        # 用例级别
        case_level = self.rsheets.cell(row_num, 1).value
        column.append(case_level)

        # 前置条件
        prediction = self.rsheets.cell(row_num, 2).value
        column.append(prediction)

        # 测试步骤
        action = self.rsheets.cell(row_num, 3).value
        column.append(action)

        # 预期结果
        compare = self.rsheets.cell(row_num, 4).value
        column.append(compare)

        return column

    def worker(self, row_num=1):

        test_case_filename = self.path.split("/")[-1]

        if row_num <= (self.nrows - 1):
            current_column = self.column_definition(row_num)
        else:
            log.info("指定执行行号{0}, 已超过最大行数，不执行.".format(row_num))
            return False

        case_name = current_column[0]
        while len(case_name.strip()) > 0:

            # 定义字体类型1. 字体：红色
            font0 = xlwt.Font()
            font0.colour_index = 2
            font0.bold = True

            style0 = xlwt.XFStyle()
            style0.font = font0

            # 定义字体类型2. 字体：蓝色
            font1 = xlwt.Font()
            font1.colour_index = 4
            font1.bold = True

            style1 = xlwt.XFStyle()
            style1.font = font1

            # 定义字体类型3. 字体：绿色
            font2 = xlwt.Font()
            font2.colour_index = 3
            font2.bold = True

            style2 = xlwt.XFStyle()
            style2.font = font2

            # 设置单元格自动换行
            style3 = xlwt.XFStyle()
            style3.alignment.wrap = 1

            self.case_file_result["pass_num"] = self.successNum
            self.case_file_result["fail_num"] = self.failNum
            self.case_file_result["skip_num"] = self.skipNum

            log.info(">>>>> %s" % case_name)

            if case_name.find("UNTEST") > -1:  # 本行不执行
                self.wsheets.write(row_num, 5, "NO TEST", style0)
                self.wsheets.write(row_num, 6, "")
                self.wsheets.write(row_num, 7, "")
                self.wsheets.write(row_num, 8, "")
                self.wbook.save(self.path)
                row_num += 1
                # 重新获取新一行的用例
                current_column = self.column_definition(row_num)
                case_name = current_column[0]
                log.info("第{0}行用例不执行，跳过\n".format(row_num - 1))
                # 跳过执行数递增
                self.skipNum += 1
                self.case_file_result.update({"skip_num": self.skipNum})
            else:
                if gbl.service.get("RunAllTest"):
                    pass
                else:
                    # 判断当前测试用例的级别是否在测试范围内
                    if current_column[1] and current_column[1] not in gbl.service.get("RunTestLevel"):
                        self.wsheets.write(row_num, 5, "NO TEST", style0)
                        self.wsheets.write(row_num, 6, "")
                        self.wsheets.write(row_num, 7, "")
                        self.wsheets.write(row_num, 8, "")
                        self.wbook.save(self.path)
                        log.info("第{0}行用例级别较低，不执行，跳过".format(row_num - 1))
                        # 跳过执行数递增
                        self.skipNum += 1
                        self.case_file_result.update({"skip_num": self.skipNum})

                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            continue
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            self.run_info[test_case_filename] = self.case_file_result
                            break

                self.wsheets.write(row_num, 5, "RUNNING", style2)
                self.wsheets.write(row_num, 6, "")
                self.wsheets.write(row_num, 7, "")
                self.wsheets.write(row_num, 8, "")
                self.wbook.save(self.path)

                # 开始测试前，数据清理
                Initiation.clear_var()

                # 设置用例执行开始时间
                gbl.temp.set("StartTime", datetime.now().strftime('%Y%m%d%H%M%S'))

                """
                1、通过preconditions执行测试用例，如果不报错，会返回True/False。
                    a) 如果True，继续执行操作步骤；
                    b) 如果False，保存用例错误信息，并根据continueRunWhenError判断是否继续执行下一条
                    c) 如果出现异常，记录exception，并按b继续
                """
                # 执行前置条件
                result = None
                # noinspection PyBroadException
                try:
                    result = preconditions(action=current_column[2])
                except Exception:
                    traceback.print_exc()
                if not result:
                    # log.info("错误信息: {0}".format(gbl.temp.get("ErrorMsg")))
                    log.error("第{0}行用例执行不通过,预置条件执行失败.\n".format(row_num))
                    self.wsheets.write(row_num, 5, "FAIL", style0)
                    self.wsheets.write(row_num, 6, gbl.temp.get("ErrorMsg"))
                    self.wsheets.write(row_num, 7, gbl.temp.get("StartTime"))
                    self.wsheets.write(row_num, 8, gbl.temp.get("EndTime"))
                    self.wbook.save(self.path)
                    # 执行失败数递增
                    self.failNum += 1
                    self.case_file_result.update({"fail_num": self.failNum})

                    if gbl.service.get("ContinueRunWhenError"):
                        gbl.service.get("browser").refresh()
                        row_num += 1
                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            case_name = current_column[9]
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            self.run_info[test_case_filename] = self.case_file_result
                            break
                        continue
                    else:
                        self.run_info[test_case_filename] = self.case_file_result
                        break

                """
                2、通过basic_run执行测试用例，如果不报错，会返回True/False。
                    a) 如果True，继续执行操作步骤；
                    b) 如果False，保存用例错误信息，并根据continueRunWhenError判断是否继续执行下一条
                    c) 如果出现异常，记录exception，并按b继续
                    d) 失败需要截图
                """
                # 执行操作步骤
                result = None
                # noinspection PyBroadException
                try:
                    result = basic_run(steps=current_column[3])
                except Exception:
                    traceback.print_exc()
                if not result:
                    # log.info("错误信息: {0}".format(gbl.temp.get("ErrorMsg")))
                    log.error("第{0}行用例执行不通过,操作步骤执行失败.".format(row_num))
                    self.wsheets.write(row_num, 5, "FAIL", style0)
                    self.wsheets.write(row_num, 6, gbl.temp.get("ErrorMsg"))
                    self.wsheets.write(row_num, 7, gbl.temp.get("StartTime"))
                    self.wsheets.write(row_num, 8, gbl.temp.get("EndTime"))
                    self.wbook.save(self.path)
                    # 执行失败数递增
                    self.failNum += 1
                    self.case_file_result.update({"fail_num": self.failNum})

                    if gbl.service.get("ContinueRunWhenError"):
                        gbl.service.get("browser").refresh()
                        row_num += 1
                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            case_name = current_column[0]
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            self.run_info[test_case_filename] = self.case_file_result
                            break
                        continue
                    else:
                        self.run_info[test_case_filename] = self.case_file_result
                        break

                """
                2、通过compare_data执行测试用例，如果不报错，会返回True/False。
                    a) 如果True，继续执行操作步骤；
                    b) 如果False，保存用例错误信息，并根据continueRunWhenError判断是否继续执行下一条
                    c) 如果出现异常，记录exception，并按b继续
                """
                # 结果校验
                result = None
                # noinspection PyBroadException
                try:
                    data_check = current_column[4]
                    result = compare_data(data_check)
                except Exception:
                    traceback.print_exc()
                if result:
                    self.wsheets.write(row_num, 5, "PASS", style1)
                    self.wsheets.write(row_num, 6, "")
                    self.wsheets.write(row_num, 7, gbl.temp.get("StartTime"))
                    self.wsheets.write(row_num, 8, gbl.temp.get("EndTime"))
                    self.wbook.save(self.path)
                    log.info("第{0}行用例执行成功！".format(row_num))
                    # 执行成功数递增
                    self.successNum += 1
                    self.case_file_result.update({"pass_num": self.successNum})
                    log.info("已经成功执行{0}条用例！\n".format(self.successNum))

                    # # 如果是AiSee操作，不宜刷新页面，页面一刷新就要重新从menu进入
                    # if get_global_var("Application") == "AiSee":
                    #     pass
                    # else:
                    gbl.service.get("browser").refresh()
                else:
                    # log.info("错误信息: {0}".format(gbl.temp.get("ErrorMsg")))
                    log.error("第{0}行用例执行不通过,结果比对失败.".format(row_num))
                    self.wsheets.write(row_num, 5, "FAIL", style0)
                    self.wsheets.write(row_num, 6, gbl.temp.get("ErrorMsg"), style3)
                    self.wsheets.write(row_num, 7, gbl.temp.get("StartTime"))
                    self.wsheets.write(row_num, 8, gbl.temp.get("EndTime"))
                    self.wbook.save(self.path)
                    log.info("！！！警告：此条测试用例执行失败！\n")
                    # 执行失败数递增
                    self.failNum += 1
                    self.case_file_result.update({"fail_num": self.failNum})

                    if gbl.service.get("ContinueRunWhenError"):
                        gbl.service.get("browser").refresh()
                        row_num += 1
                        if row_num <= (self.nrows - 1):
                            # 重新获取新一行的用例
                            current_column = self.column_definition(row_num)
                            case_name = current_column[0]
                        else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                            self.run_info[test_case_filename] = self.case_file_result
                            break
                        continue
                    else:
                        self.run_info[test_case_filename] = self.case_file_result
                        break

                # 预置条件、操作步骤、比对结果完成后进行操作
                row_num += 1
                self.wbook.save(self.path)
                if row_num <= (self.nrows - 1):
                    # 重新获取新一行的用例
                    current_column = self.column_definition(row_num)
                    case_name = current_column[0]
                else:  # 执行完最后一条用例，跳出循环，打印执行结果。
                    self.run_info[test_case_filename] = self.case_file_result
                    break
            self.run_info[test_case_filename] = self.case_file_result

        log.info("本用例集全部用例执行完成。执行结果：")
        log.info("执行成功数 | %d |" % self.successNum)
        log.info("执行失败数 | %d |" % self.failNum)
        log.info("跳过用例数 | %d |\n" % self.skipNum)
        self.to_end = True
        return False if self.failNum > 0 else True
