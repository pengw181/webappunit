# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/21 上午10:37

from time import sleep
from selenium.webdriver.common.by import By
from src.main.python.core.app.VisualModeler.process.node.oprt.loop import condition
from src.main.python.lib.processVar import choose_var
from src.main.python.lib.logger import log
from src.main.python.lib.globalVariable import *


def aggregate(input_var, group_by, expression, output_var, output_col, value_type, transpose):
    # 聚合运算
    """
    :param input_var: 选择变量，必填
    :param group_by: 分组依据，必填
    :param expression: 表达式，字典，必填
    :param output_var: 输出名称，字典，必填
    :param output_col: 输出列，多列以逗号分隔，非必填
    :param value_type: 赋值方式，替换/追加，非必填
    :param transpose: 是否转置，bool

    {
        "选择变量": "时间",
        "分组依据": "1",
        "表达式": [
            ["总计(sum)", "1"]
        ],
        "输出名称": {
            "类型": "输入",
            "变量名": "聚合运算总计结果"
        },
        "输出列": "*",
        "赋值方式": "替换",
        "是否转置": "否"
    }
    ["总计(sum)", "1"]
    ["计数(count)", "1"]
    ["最大值(max)", "1"]
    ["最小值(min)", "1"]
    ["平均值(avg)", "1"]
    ["分组连接", "2,&"]
    """
    browser = get_global_var("browser")
    # 切换到过滤运算iframe
    browser.switch_to.frame(browser.find_element(By.XPATH, "//iframe[contains(@src,'operateCfgAgg.html')]"))

    # 选择变量
    if input_var:
        browser.find_element(By.XPATH, "//*[@id='dataH_inputVarName']/following-sibling::span//a").click()
        choose_var(var_name=input_var)
        log.info("选择变量: {0}".format(input_var))
        sleep(1)

    # 表达式
    if expression:
        condition(array=expression, basic_cal=True)
        log.info("表达式配置完成")
        sleep(1)

    # 分组依据
    if group_by:
        browser.find_element(By.XPATH, "//*[@name='groupBy']/preceding-sibling::input").send_keys(group_by)
        log.info("设置分组依据: {0}".format(group_by))
        sleep(1)

    # 输出名称
    if output_var:
        output_var_type = output_var.get("类型")
        output_var_value = output_var.get("变量名")
        if output_var_type == "输入":
            out_var_element = browser.find_element(
                By.XPATH, "//*[@id='dataH_resultBaseVarName']/following-sibling::span//input[1]")
            browser.execute_script("arguments[0].scrollIntoView(true);", out_var_element)
            out_var_element.send_keys(output_var_value)
        elif output_var_type == "选择":
            # 输出名称选择变量
            browser.find_element(By.XPATH, "//*[@id='dataH_resultBaseVarName']/following-sibling::span//a").click()
            choose_var(var_name=output_var_value)
        else:
            raise KeyError("【输出名称】类型只支持: 输入、选择")
        log.info("设置输出名称: {0}".format(output_var))
        sleep(1)

    # 输出列
    if output_col:
        browser.find_element(By.XPATH, "//*[@name='outColumn']/preceding-sibling::input").clear()
        browser.find_element(By.XPATH, "//*[@name='outColumn']/preceding-sibling::input").send_keys(output_col)
        log.info("设置输出列: {0}".format(output_var))
        sleep(1)

    # 赋值方式
    if value_type:
        elements = browser.find_elements(By.XPATH, "//*[@name='valueType']/preceding-sibling::input")
        for e1 in elements:
            if e1.is_displayed():
                e1.click()
                elements = browser.find_elements(
                    By.XPATH, "//*[contains(@id,'valuetype') and text()='{0}']".format(value_type))
                for e2 in elements:
                    if e2.is_displayed():
                        e2.click()
                        log.info("设置赋值方式: {0}".format(value_type))
                        sleep(1)
                        break

    # 是否转置
    js = 'return $("#isTranspose")[0].checked;'
    status = browser.execute_script(js)
    log.info("【是否转置】勾选状态: {0}".format(status))
    # 聚焦元素
    transpose_click = browser.find_element(By.XPATH, "//*[@id='isTranspose']")
    browser.execute_script("arguments[0].scrollIntoView(true);", transpose_click)
    if transpose:
        if not status:
            transpose_click.click()
        log.info("勾选【是否转置】")
    else:
        if status:
            transpose_click.click()
            log.info("取消勾选【是否转置】")
        else:
            log.info("【是否转置】标识为否，不开启")

    # 返回到上层iframe
    browser.switch_to.parent_frame()
