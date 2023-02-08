# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2022/8/12 下午3:53

from datetime import datetime
from src.main.python.lib.logger import log
from src.main.python.lib.globalVariable import *
from src.main.python.conf.loads import properties


def saveScreenShot():
    browser = get_global_var("browser")
    base_path = properties.get("projectBasePath") + properties.get("projectName") + properties.get("screenShotPath")
    folder_id = get_global_var("FolderID")
    screenShot_file_path = base_path + folder_id + "/"
    timestamp = datetime.strftime(datetime.now(), "%Y_%m_%d_%H_%M_%S") + str(datetime.now().microsecond)
    suffix = '.png'
    file_name = "Webdriver_" + timestamp + suffix
    screenShot_file = screenShot_file_path + file_name
    browser.save_screenshot(screenShot_file)
    log.info("保存截图: {0}".format(file_name))
    return screenShot_file
