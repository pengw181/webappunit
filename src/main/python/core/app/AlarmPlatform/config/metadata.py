# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/12/24 下午3:05

from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from src.main.python.lib.pageMaskWait import page_wait
from src.main.python.lib.input import set_textarea
from src.main.python.core.app.AlarmPlatform.menu import choose_menu
from src.main.python.lib.alertBox import BeAlertBox
from src.main.python.lib.globalVariable import *
from src.main.python.lib.logger import log


class MetaData:

    def __init__(self):
        self.browser = get_global_var("browser")
        self.upperOrLower = None
        # 进入菜单
        choose_menu("告警配置-告警元数据")
        page_wait()
        # 切换iframe
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.frame_to_be_available_and_switch_to_it((
            By.XPATH, "//iframe[contains(@src,'html/dataConfig/metadata/metadataList.html')]")))
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.element_to_be_clickable((By.XPATH, "//*[@id='metadataName']/following-sibling::span[1]/input[1]")))
        page_wait()
        sleep(1)

    def choose(self, metadata_name):
        """
        :param metadata_name: 元数据名称
        """
        input_ele = self.browser.find_element(By.XPATH, "//*[@id='metadataName']/following-sibling::span[1]/input[1]")
        input_ele.clear()
        input_ele.send_keys(metadata_name)
        self.browser.find_element(By.XPATH, "//span[text()='查询']").click()
        page_wait()
        self.browser.find_element(By.XPATH, "//*[@field='metadataName']//a[text()='{}']".format(metadata_name)).click()
        log.info("已选择元数据: {}".format(metadata_name))

    def add(self, metadata_name, database, table_belong, data_delay, remark, time_field, time_field_format,
            prepare_field, selected_field):
        """
        :param metadata_name: 元数据名称
        :param database: 数据库
        :param table_belong: 表中文名
        :param data_delay: 数据时延
        :param remark: 备注
        :param time_field: 时间字段
        :param time_field_format: 时间格式
        :param prepare_field: 待选字段，数组
        :param selected_field: 已选字段，字典
        """
        self.browser.find_element(By.XPATH, "//*[@id='addBtn']//*[text()='添加']").click()
        page_wait()
        self.browser.switch_to.parent_frame()
        wait = WebDriverWait(self.browser, 10)
        wait.until(ec.frame_to_be_available_and_switch_to_it((
            By.XPATH, "//iframe[contains(@src,'/AlarmPlatform/html/dataConfig/metadata/editMetadata.html')]")))
        sleep(1)
        self.metadata_page(metadata_name, database, table_belong, data_delay, remark, time_field, time_field_format,
                           prepare_field, selected_field)

        # 保存
        self.browser.find_element(By.XPATH, "//*[@id='saveButtonId']").click()
        alert = BeAlertBox()
        msg = alert.get_msg()
        if alert.title_contains("提交成功"):
            log.info("数据 {0} 添加成功".format(metadata_name))
        else:
            log.warning("数据 {0} 添加失败，失败提示: {1}".format(metadata_name, msg))
        set_global_var("ResultMsg", msg, False)

    def update(self, obj, metadata_name, data_delay, remark, prepare_field, selected_field):
        """
        :param obj: 元数据名称
        :param metadata_name: 元数据名称
        :param data_delay: 数据时延
        :param remark: 备注
        :param prepare_field: 待选字段，数组
        :param selected_field: 已选字段，字典
        """
        log.info("开始修改数据")
        self.choose(obj)
        self.browser.find_element(By.XPATH, "//*[text()='修改']").click()
        self.browser.switch_to.parent_frame()
        wait = WebDriverWait(self.browser, 10)
        wait.until(ec.frame_to_be_available_and_switch_to_it((
            By.XPATH, "//iframe[contains(@src,'/AlarmPlatform/html/dataConfig/metadata/editMetadata.html')]")))
        sleep(1)
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.element_to_be_clickable((
            By.XPATH, "//*[@id='editDiv']//*[@id='metadataName']/following-sibling::span/input[1]")))

        self.metadata_page(metadata_name, None, None, data_delay, remark, None, None, prepare_field,
                           selected_field)

        # 保存
        self.browser.find_element(By.XPATH, "//*[@id='saveButtonId']").click()
        alert = BeAlertBox()
        msg = alert.get_msg()
        if alert.title_contains("提交成功"):
            log.info("{0} 修改成功".format(obj))
        else:
            log.warning("{0} 修改失败，失败提示: {1}".format(obj, msg))
        set_global_var("ResultMsg", msg, False)

    def metadata_page(self, metadata_name, database, table_belong, data_delay, remark, time_field, time_field_format,
                      prepare_field, selected_field):
        """
        :param metadata_name: 元数据名称
        :param database: 数据库
        :param table_belong: 表中文名
        :param data_delay: 数据时延
        :param remark: 备注
        :param time_field: 时间字段
        :param time_field_format: 时间格式
        :param prepare_field: 待选字段，数组
        :param selected_field: 已选字段，字典
        """
        # 元数据名称
        if metadata_name:
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='metadataName']/following-sibling::span/input[1]").clear()
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='metadataName']/following-sibling::span/input[1]").send_keys(
                metadata_name)
            log.info("设置元数据名称: {0}".format(metadata_name))

        # 数据库
        if database:
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='databaseInfoId']/following-sibling::span/input[1]").click()
            sleep(1)
            self.browser.find_element(
                By.XPATH, "//*[contains(@id,'databaseInfoId') and text()='{}']".format(database)).click()
            log.info("设置数据库: {0}".format(database))

        # 表中文名
        if table_belong:
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='tableBelongId']/following-sibling::span/input[1]").click()
            sleep(1)
            self.browser.find_element(
                By.XPATH, "//*[contains(@id,'tableBelongId') and text()='{}']".format(table_belong)).click()
            log.info("设置表中文名: {0}".format(table_belong))
            # 等待表字段加载
            wait = WebDriverWait(self.browser, 10)
            wait.until(ec.element_to_be_clickable((By.XPATH, "//*[contains(@id,'prepareFieldAreaDiv')]//*[text()='1']")))
            sleep(1)

        # 根据加载的待选字段，判断当前数据库返回的是大写或小写
        data_col_obj = self.browser.find_element(
            By.XPATH, "//*[contains(@id,'prepareFieldAreaDiv') and @datagrid-row-index='0']/*[@field='COLUMN_NAME']/div")
        col_temp = data_col_obj.get_attribute("innerText")
        if col_temp == col_temp.lower():
            self.upperOrLower = "lower"
            log.info("表【{0}】返回字段小写".format(table_belong))
        else:
            self.upperOrLower = "upper"
            log.info("表【{0}】返回字段大写".format(table_belong))
        set_global_var("UpperOrLower", self.upperOrLower, False)

        # 数据时延
        if data_delay:
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='dataDelay']/following-sibling::span/input[1]").clear()
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='dataDelay']/following-sibling::span/input[1]").send_keys(data_delay)
            log.info("设置数据时延: {0}".format(data_delay))

        # 备注
        if remark:
            remark_textarea = self.browser.find_element(By.XPATH, "//*[@id='remark']")
            set_textarea(remark_textarea, remark)
            log.info("设置备注: {0}".format(remark))

        # 时间字段
        if time_field:
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='timeField']/following-sibling::span/input[1]").click()
            sleep(1)
            # 字段自动转换
            if self.upperOrLower == "upper":
                time_field = time_field.upper()
            else:
                time_field = time_field.lower()

            self.browser.find_element(
                By.XPATH, "//*[contains(@id,'timeField') and text()='{}']".format(time_field)).click()
            log.info("设置时间字段: {0}".format(time_field))

        # 时间格式
        if time_field_format:
            self.browser.find_element(
                By.XPATH, "//*[@id='editDiv']//*[@id='timeFieldType']/following-sibling::span/input[1]").click()
            sleep(1)
            self.browser.find_element(
                By.XPATH, "//*[contains(@id,'timeFieldType') and text()='{}']".format(time_field_format)).click()
            log.info("设置时间格式: {0}".format(time_field_format))

        # 待选字段
        if prepare_field:
            # 先清空已被选择字段
            selected_ele = self.browser.find_elements(
                By.XPATH, "//*[@id='prepareFieldAreaDivRow']/div/div[2]/div/div[2]//*[contains(@id,'prepareFieldAreaDiv') "
                          "and contains(@class,'selected')]")
            if len(selected_ele) > 0:
                for s in selected_ele:
                    s.click()
                log.info("清空已被选择字段")
                sleep(1)
            # 重新选择字段
            for p in prepare_field:
                # 字段自动转换
                if self.upperOrLower == "upper":
                    p = p.upper()
                else:
                    p = p.lower()
                to_selected_field = self.browser.find_element(
                    By.XPATH, "//*[contains(@class,'COLUMN_NAME') and text()='{0}']".format(p))
                self.browser.execute_script("arguments[0].scrollIntoView(true);", to_selected_field)
                to_selected_field.click()
                log.info("选择待选字段: {0}".format(p))

        # 已选字段
        if selected_field:
            if isinstance(selected_field, dict):
                for key, value in selected_field.items():
                    # 字段自动转换
                    if self.upperOrLower == "upper":
                        key = key.upper()
                    else:
                        key = key.lower()
                    self.browser.find_element(
                        By.XPATH, "//*[contains(@class,'colNameEn') and text()='{0}']/../following-sibling::td[4]//*[text()='编辑']".format(
                            key)).click()
                    b_name = value.get("字段别名")
                    d_name = value.get("显示名称")
                    if self.upperOrLower == "upper":
                        b_name = b_name.upper()
                        d_name = d_name.upper()
                    else:
                        b_name = b_name.lower()
                        d_name = d_name.lower()
                    if b_name:
                        self.browser.find_element(
                            By.XPATH, "//*[contains(@class,'colNameEn') and text()='{0}']/../following-sibling::td[1]//input".format(
                                key)).clear()
                        self.browser.find_element(
                            By.XPATH, "//*[contains(@class,'colNameEn') and text()='{0}']/../following-sibling::td[1]//input".format(
                                key)).send_keys(b_name)
                    if d_name:
                        self.browser.find_element(
                            By.XPATH, "//*[contains(@class,'colNameEn') and text()='{0}']/../following-sibling::td[2]//input".format(
                                key)).clear()
                        self.browser.find_element(
                            By.XPATH, "//*[contains(@class,'colNameEn') and text()='{0}']/../following-sibling::td[2]//input".format(
                                key)).send_keys(d_name)
                    self.browser.find_element(
                        By.XPATH, "//*[contains(@class,'colNameEn') and text()='{0}']/../following-sibling::td[4]//*[text()='确定']".format(
                            key)).click()
                    log.info("{0}设置完成".format(key))
            else:
                raise KeyError("已选字段不是字典格式")

    def delete(self, metadata_name):
        """
        :param metadata_name: 元数据名称
        """
        log.info("开始删除数据")
        self.choose(metadata_name)
        self.browser.find_element(By.XPATH, "//*[text()='删除']").click()

        alert = BeAlertBox(back_iframe=False)
        msg = alert.get_msg()
        if alert.title_contains(metadata_name, auto_click_ok=False):
            alert.click_ok()
            sleep(1)
            alert = BeAlertBox(back_iframe=False)
            msg = alert.get_msg()
            if alert.title_contains("成功"):
                log.info("{0} 删除成功".format(metadata_name))
            else:
                log.warning("{0} 删除失败，失败提示: {1}".format(metadata_name, msg))
        else:
            log.warning("{0} 删除失败，失败提示: {1}".format(metadata_name, msg))
        set_global_var("ResultMsg", msg, False)

    def data_clear(self, metadata_name, fuzzy_match=False):
        """
        :param metadata_name: 元数据名称
        :param fuzzy_match: 模糊匹配
        """
        # 用于清除数据，在测试之前执行, 使用关键字开头模糊查询
        self.browser.find_element(By.XPATH, "//*[@id='metadataName']/following-sibling::span[1]/input[1]").clear()
        self.browser.find_element(By.XPATH, "//*[@id='metadataName']/following-sibling::span[1]/input[1]").send_keys(metadata_name)
        self.browser.find_element(By.XPATH, "//*[@id='btn']//*[text()='查询']").click()
        page_wait()
        fuzzy_match = True if fuzzy_match == "是" else False
        if fuzzy_match:
            record_element = self.browser.find_elements(
                By.XPATH, "//*[@field='metadataName']/*[contains(@class,'metadataName')]/*[starts-with(text(),'{}')]".format(
                    metadata_name))
        else:
            record_element = self.browser.find_elements(
                By.XPATH, "//*[@field='metadataName']/*[contains(@class,'metadataName')]/*[text()='{}']".format(metadata_name))
        if len(record_element) > 0:
            exist_data = True

            while exist_data:
                pe = record_element[0]
                search_result = pe.text
                pe.click()
                log.info("选择: {0}".format(search_result))
                # 删除
                self.browser.find_element(By.XPATH, "//*[text()='删除']").click()
                alert = BeAlertBox(back_iframe=False)
                msg = alert.get_msg()
                if alert.title_contains("您确定需要删除{0}吗".format(search_result), auto_click_ok=False):
                    alert.click_ok()
                    alert = BeAlertBox(back_iframe=False)
                    msg = alert.get_msg()
                    if alert.title_contains("成功"):
                        log.info("{0} 删除成功".format(search_result))
                        page_wait()
                        if fuzzy_match:
                            # 重新获取页面查询结果
                            record_element = self.browser.find_elements(
                                By.XPATH, "//*[@field='metadataName']/*[contains(@class,'metadataName')]/*[starts-with(text(),'{0}')]".format(
                                    metadata_name))
                            if len(record_element) > 0:
                                exist_data = True
                            else:
                                # 查询结果为空,修改exist_data为False，退出循环
                                log.info("数据清理完成")
                                exist_data = False
                        else:
                            break
                    else:
                        raise Exception("删除数据时出现未知异常: {0}".format(msg))
                else:
                    # 无权操作
                    log.warning("{0} 清理失败，失败提示: {1}".format(metadata_name, msg))
                    set_global_var("ResultMsg", msg, False)
                    break
        else:
            # 查询结果为空,结束处理
            log.info("查询不到满足条件的数据，无需清理")
