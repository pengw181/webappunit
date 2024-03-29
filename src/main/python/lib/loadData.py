# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/11/8 下午3:33

from src.main.python.lib.logger import log
from src.main.python.lib.globals import gbl


def load_sample(sample_file_name):
    file_path = gbl.service.get("ProjectPath") + '/src/main/resources/sample_data/' + sample_file_name
    log.info("从{}加载sample数据".format(file_path))
    content = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            content.append(line)
    return content


if __name__ == "__main__":
    file_content = load_sample("ping_sample.txt")
    log.info(file_content)
