# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/9/17 下午4:05

from time import sleep
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from src.main.python.lib.pageMaskWait import page_wait
from src.main.python.core.app.AiSee.netunit.menu import choose_menu
from src.main.python.lib.alertBox import BeAlertBox
from src.main.python.lib.logger import log
from src.main.python.lib.globals import gbl


class Template(object):

    def __init__(self):
        self.browser = gbl.service.get("browser")
        choose_menu(menu="统一网元配置")

        # 切到统一网元配置页面
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.frame_to_be_available_and_switch_to_it((
            By.XPATH, "//*[contains(@src,'/html/nu/midJumpBatchCfgInfo.html')]")))
        page_wait()
        sleep(1)

    def choose(self, template_name):
        """
        :param template_name: 模版名称
        """
        input_ele = self.browser.find_element(By.XPATH, "//*[@id='tempName']/following-sibling::span/input[1]")
        input_ele.clear()
        input_ele.send_keys(template_name)
        self.browser.find_element(By.XPATH, "//*[@id='btn']").click()
        page_wait()
        self.browser.find_element(By.XPATH, "//*[@field='tempName']//*[@data-mtips='{}']".format(template_name)).click()
        log.info("已选模版: {}".format(template_name))

    def add(self, template_name, netunit_type, login_type, remark, login_set):
        """
        :param template_name: 模版名称
        :param netunit_type: 网元类型
        :param login_type: 登录模式
        :param remark: 用途说明
        :param login_set: 登录配置
        """
        self.browser.find_element(By.XPATH, "//*[@id='addBtn']//*[text()='添加']").click()
        self.browser.switch_to.frame(
            self.browser.find_element(By.XPATH, "//iframe[contains(@src,'midJumpBatchCfgInfoEdit.html?type=add')]"))
        sleep(1)
        self.template_page(template_name=template_name, netunit_type=netunit_type, login_type=login_type,
                           remark=remark, login_set=login_set)

        # 提交
        self.browser.find_element(By.XPATH, "//*[@id='saveBtn']").click()
        alert = BeAlertBox(back_iframe="default")
        msg = alert.get_msg()
        if alert.title_contains("保存成功"):
            log.info("保存配置成功")
        else:
            log.warning("保存配置失败，失败提示: {0}".format(msg))
            alert.click_ok()
        gbl.temp.set("ResultMsg", msg)

    def update(self, obj_template, template_name, netunit_type, login_type, remark, login_set):
        """
        :param obj_template: 目标模版名称
        :param template_name: 模版名称
        :param netunit_type: 网元类型
        :param login_type: 登录模式
        :param remark: 用途说明
        :param login_set: 登录配置
        """
        self.choose(template_name=obj_template)
        self.browser.find_element(By.XPATH, "//*[@id='editBtn']").click()
        alert = BeAlertBox(back_iframe=False, timeout=1)
        exist = alert.exist_alert
        if exist:
            msg = alert.get_msg()
            gbl.temp.set("ResultMsg", msg)
        else:
            # 切换iframe
            wait = WebDriverWait(self.browser, 30)
            wait.until(ec.frame_to_be_available_and_switch_to_it((
                By.XPATH, "//iframe[contains(@src,'netunitInfoEdit.html?type=edit')]")))
            sleep(1)
            wait = WebDriverWait(self.browser, 30)
            wait.until(ec.element_to_be_clickable((By.XPATH, "//*[@name='ip']/preceding-sibling::input")))
            self.template_page(template_name=template_name, netunit_type=netunit_type, login_type=login_type,
                               remark=remark, login_set=login_set)

            # 提交
            self.browser.find_element(By.XPATH, "//*[@id='saveBtn']").click()
            alert = BeAlertBox(back_iframe="default")
            msg = alert.get_msg()
            if alert.title_contains("保存成功"):
                log.info("保存配置成功")
            else:
                log.warning("保存配置失败，失败提示: {0}".format(msg))
                alert.click_ok()
            gbl.temp.set("ResultMsg", msg)

    def template_page(self, template_name, netunit_type, login_type, remark, login_set):
        """
        :param template_name: 模版名称
        :param netunit_type: 网元类型
        :param login_type: 登录模式
        :param remark: 用途说明
        :param login_set: 登录配置
        """
        # 模版名称
        if template_name:
            self.browser.find_element(By.XPATH, "//*[@name='tempName']/preceding-sibling::input").clear()
            self.browser.find_element(By.XPATH, "//*[@name='tempName']/preceding-sibling::input").send_keys(
                template_name)
            log.info("设置模版名称: {}".format(template_name))

        # 网元类型
        if netunit_type:
            self.browser.find_element(By.XPATH, "//*[@id='levelId']/following-sibling::span//a").click()
            sleep(1)
            type_list = self.browser.find_element(
                By.XPATH, "//*[contains(@id,'levelId') and text()='{}']".format(netunit_type))
            action = ActionChains(self.browser)
            action.move_to_element(type_list).click().perform()
            log.info("设置网元类型: {}".format(netunit_type))

        # 登录模式
        if login_type:
            self.browser.find_element(By.XPATH, "//*[@id='loginTypeId']/following-sibling::span//a").click()
            sleep(1)
            type_list = self.browser.find_element(
                By.XPATH, "//*[contains(@id,'loginTypeId') and text()='{}']".format(login_type))
            action = ActionChains(self.browser)
            action.move_to_element(type_list).click().perform()
            log.info("设置登录模式: {}".format(login_type))

        # 用途说明
        if remark:
            self.browser.find_element(By.XPATH, "//*[@name='remark']/preceding-sibling::input").clear()
            self.browser.find_element(By.XPATH, "//*[@name='remark']/preceding-sibling::input").send_keys(remark)
            log.info("设置用途说明: {}".format(remark))

        # 登录配置
        if login_set:
            login_cmd_field = "//*[@id='tb']/following-sibling::div[1]"
            row_num = 1

            for ls in login_set:
                try:
                    row_ele = self.browser.find_element(
                        By.XPATH, login_cmd_field + "/div[2]/div[2]//tr[{}]/*[@field='customId']//input[contains(@id,'textbox')]".format(
                            row_num))
                    # 如果已存在，则单击修改
                    action = ActionChains(self.browser)
                    action.move_to_element(row_ele).click().perform()
                    sleep(1)
                except NoSuchElementException:
                    # 如果不存在，则点击添加按钮
                    self.browser.find_element(By.XPATH, "//*[@onclick='appendCmd()']").click()
                finally:
                    self.browser.find_element(
                        By.XPATH, login_cmd_field + "/div[2]/div[2]//tr[{}]/*[@field='customId']//input[contains(@id,'textbox')]".format(
                            row_num)).click()
                    jump_step_list = self.browser.find_element(
                        By.XPATH, "//*[contains(@id,'_easyui_combobox_') and text()='{}']".format(ls))
                    action = ActionChains(self.browser)
                    action.move_to_element(jump_step_list).click().perform()
                    log.info("设置登录指令名称: {}".format(ls))
                    row_num += 1

    def delete(self, obj_template):
        """
        :param obj_template: 目标模版名称
        :return:
        """
        self.choose(template_name=obj_template)
        self.browser.find_element(By.XPATH, "//*[@id='deleteBtn']").click()
        alert = BeAlertBox(back_iframe=False)
        msg = alert.get_msg()
        if alert.title_contains(obj_template, auto_click_ok=False):
            alert.click_ok()
            sleep(1)
            alert = BeAlertBox(back_iframe=False)
            msg = alert.get_msg()
            if alert.title_contains("成功"):
                log.info("{0} 删除成功".format(obj_template))
            else:
                log.warning("{0} 删除失败，失败提示: {1}".format(obj_template, msg))
        else:
            log.warning("{0} 删除失败，失败提示: {1}".format(obj_template, msg))
        gbl.temp.set("ResultMsg", msg)

    def bind_netunit(self, obj_template, condition, assign_type, netunit_list=None):
        """
        :param obj_template: 目标模版名称
        :param condition: 查询条件
        :param netunit_list: 网元列表
        :param assign_type: 分配方式
        """
        # 点击网元绑定
        self.browser.find_element(
            By.XPATH, "//*[@data-mtips='{}']/../../following-sibling::td[4]//a[text()='网元绑定']".format(obj_template)).click()

        # 切换到绑定网元页面iframe
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.frame_to_be_available_and_switch_to_it((
            By.XPATH, "//iframe[contains(@src,'midJumpBatchCfgInfoNetunitQuote.html?type=edit')]")))
        sleep(1)
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.element_to_be_clickable((By.XPATH, "//*[@name='netunitName']/preceding-sibling::input")))

        # 网元名称
        if condition.__contains__("网元名称"):
            netunit_name = condition.get("网元名称")
            self.browser.find_element(By.XPATH, "//*[@id='netunitName']/following-sibling::span/input[1]").clear()
            self.browser.find_element(
                By.XPATH, "//*[@id='netunitName']/following-sibling::span/input[1]").send_keys(netunit_name)
            log.info("网元名称输入关键字: {}".format(netunit_name))

        # 生产厂家
        if condition.__contains__("生产厂家"):
            vendor = condition.get("生产厂家")
            self.browser.find_element(By.XPATH, "//*[@id='vendorId']/following-sibling::span//a").click()
            vendor_list = self.browser.find_element(
                By.XPATH, "//*[contains(@id,'vendorId') and text()='{}']".format(vendor))
            action = ActionChains(self.browser)
            action.move_to_element(vendor_list).click().perform()
            log.info("生产厂家选择: {}".format(vendor))

        # 设备型号
        if condition.__contains__("设备型号"):
            netunit_model = condition.get("设备型号")
            self.browser.find_element(By.XPATH, "//*[@id='netunitModelId']/following-sibling::span/input[1]").clear()
            self.browser.find_element(
                By.XPATH, "//*[@id='netunitModelId']/following-sibling::span/input[1]").send_keys(netunit_model)
            log.info("设备型号输入关键字: {}".format(netunit_model))

        self.browser.find_element(By.XPATH, "//*[@id='searchBtn1']//span[text()='查询待选择']").click()
        page_wait(timeout=180)

        # 分配方式
        if assign_type == "分配全部":
            if condition is None:
                log.warning("绑定所有网元时，需要指定分配网元列表")
            else:
                self.browser.find_element(By.XPATH, "//*[@id='allToQuoted']").click()
                alert = BeAlertBox(back_iframe="default")
                msg = alert.get_msg()
                if alert.title_contains("您确定需要分配全部数据吗", auto_click_ok=False):
                    alert.click_ok()
                    sleep(1)
                    alert = BeAlertBox(back_iframe=False)
                    msg = alert.get_msg()
                    if alert.title_contains("分配成功"):
                        log.info("网元分配成功")
                    else:
                        log.warning("网元分配失败，失败提示: {}".format(msg))
                else:
                    log.warning("网元分配失败，失败提示: {}".format(msg))
                gbl.temp.set("ResultMsg", msg)

        elif assign_type == "分配所选":
            if netunit_list is None:
                log.warning("绑定所选网元时，需要指定分配网元列表")
            else:
                for n in netunit_list:
                    self.browser.find_element(
                        By.XPATH, "//*[@class='middle']/preceding-sibling::div[1]//*[@field='netunitName']/*[text()='{}']".format(
                            n)).click()
                    log.info("待分配列表选择网元: {}".format(n))
                self.browser.find_element(By.XPATH, "//*[@id='allToQuoted']").click()
                alert = BeAlertBox(back_iframe="default")
                msg = alert.get_msg()
                if alert.title_contains("您确定需要分配全部数据吗", auto_click_ok=False):
                    alert.click_ok()
                    sleep(1)
                    alert = BeAlertBox(back_iframe=False)
                    msg = alert.get_msg()
                    if alert.title_contains("分配成功"):
                        log.info("网元分配成功")
                    else:
                        log.warning("网元分配失败，失败提示: {}".format(msg))
                else:
                    log.warning("网元分配失败，失败提示: {}".format(msg))
                gbl.temp.set("ResultMsg", msg)

        elif assign_type == "移除全部":
            self.browser.find_element(By.XPATH, "//*[@id='allToQuoted']").click()
            alert = BeAlertBox(back_iframe="default")
            msg = alert.get_msg()
            if alert.title_contains("您确定需要分配全部数据吗", auto_click_ok=False):
                alert.click_ok()
                sleep(1)
                alert = BeAlertBox(back_iframe=False)
                msg = alert.get_msg()
                if alert.title_contains("移除成功"):
                    log.info("网元移除成功")
                else:
                    log.warning("网元移除失败，失败提示: {}".format(msg))
            else:
                log.warning("网元移除失败，失败提示: {}".format(msg))
            gbl.temp.set("ResultMsg", msg)

        elif assign_type == "移除所选":
            if netunit_list is None:
                log.warning("绑定所选网元时，需要指定分配网元列表")
            else:
                for n in netunit_list:
                    self.browser.find_element(
                        By.XPATH, "//*[@class='middle']/following-sibling::div[1]//*[@field='netunitName']/*[text()='{}']".format(
                            n)).click()
                    log.info("已分配列表选择网元: {}".format(n))
                self.browser.find_element(By.XPATH, "//*[@id='allToQuoted']").click()
                alert = BeAlertBox(back_iframe="default")
                msg = alert.get_msg()
                if alert.title_contains("您确定需要分配全部数据吗", auto_click_ok=False):
                    alert.click_ok()
                    sleep(1)
                    alert = BeAlertBox(back_iframe=False)
                    msg = alert.get_msg()
                    if alert.title_contains("移除成功"):
                        log.info("网元移除成功")
                    else:
                        log.warning("网元移除失败，失败提示: {}".format(msg))
                else:
                    log.warning("网元移除失败，失败提示: {}".format(msg))
                gbl.temp.set("ResultMsg", msg)

        else:
            log.error("网元分配方式仅支持：分配全部、分配所选、移除全部、移除所选")

        # 重新进入到该页面iframe，方便循环操作
        self.browser.switch_to.frame(
            self.browser.find_element(By.XPATH, "//iframe[contains(@src,'/AiSee/html/nu/netunitMgtIndex.html')]"))
        self.browser.switch_to.frame(
            self.browser.find_element(By.XPATH, "//iframe[contains(@src,'/html/nu/midJumpBatchCfgInfo.html')]"))
        self.browser.switch_to.frame(
            self.browser.find_element(By.XPATH, "//iframe[contains(@src,'midJumpBatchCfgInfoNetunitQuote.html')]"))
        sleep(1)

    def delivery(self, obj_template):
        """
        :param obj_template: 目标模版名称
        :return:
        """
        # 点击配置下发
        self.browser.find_element(
            By.XPATH, "//*[@data-mtips='{}']/../../following-sibling::td[4]//a[text()='配置下发']".format(obj_template)).click()

        # 切换到配置下发页面iframe
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.frame_to_be_available_and_switch_to_it((
            By.XPATH, "//iframe[contains(@src,'midJumpBatchCfgInfoNetunitConfirm.html?type=edit')]")))
        sleep(1)

        # 点击确认下发
        wait = WebDriverWait(self.browser, 30)
        wait.until(ec.element_to_be_clickable((By.XPATH, "//*[@id='btn']")))
        # 下发过程需等待片刻
        page_wait(timeout=180)
        alert = BeAlertBox(back_iframe="default")
        msg = alert.get_msg()
        if alert.title_contains("请到“登录配置确认”页面确认更改内容"):
            log.info("网元配置下发成功")
        else:
            log.warning("网元配置下发失败，失败提示: {}".format(msg))
            alert.click_ok()
        gbl.temp.set("ResultMsg", msg)
