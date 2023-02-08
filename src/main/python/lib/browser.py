# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/9/10 下午5:10


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.main.python.lib.logger import log


def initBrowser(chrome_driver_path, download_path=None):
    log.info("开始初始化浏览器.")
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': download_path}
    options.add_experimental_option('prefs', prefs)
    chrome_server = Service(chrome_driver_path)
    browser = webdriver.Chrome(service=chrome_server, options=options)
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior',
              'params': {'behavior': 'allow', 'downloadPath': download_path}}
    browser.execute("send_command", params)
    log.info("浏览器初始化完成，webdriver: {0}".format(browser))
    return browser
