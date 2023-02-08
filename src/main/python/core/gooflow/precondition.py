# -*- encoding: utf-8 -*-
# @Author: peng wei
# @Time: 2021/7/20 上午10:37

from time import sleep
from datetime import datetime
from src.main.python.db.SQLHelper import SQLUtil
from src.main.python.core.gooflow.codes import saveCode
from src.main.python.lib.globalVariable import *
from src.main.python.lib.updateData import update_json
from src.main.python.lib.logger import log
from src.main.python.conf.loads import db_config
from src.main.python.conf.loads import schema_config


def preconditions(action):
    """
    :param action: 可以设置全局变量，可以执行sql
    :return: 执行结果，true/false
    """

    # 多条sql语句按换行分隔
    if action.strip() == "":    # 预置条件为空
        run_flag = True
    else:
        pre_list = action.split(chr(10))
        run_flag = False

        # 去掉空行
        _tmp = []
        for one_pre in pre_list:
            one_pre = one_pre.strip()
            if one_pre != "":
                _tmp.append(one_pre)
        pre_list = _tmp

        # 预置条件不为空，拆成多条执行
        for i in range(len(pre_list)):
            # 替换${Database}变量
            pre_list[i] = replace_global_var(pre_list[i])

            if pre_list[i].lower().startswith("global"):
                # 变量赋值，加入到global_set
                log.info("开始设置全局变量：{0}".format(pre_list[i]))
                # noinspection PyBroadException
                try:
                    var_set = pre_list[i].split("|", 2)
                    set_global_var(var_set[1].strip(), var_set[2].strip())
                    log.info("设置全局变量：{0}成功".format(var_set[1].strip()))
                    run_flag = True
                except Exception as e:
                    saveCode("设置全局变量异常: {0}".format(str(e)))
                    run_flag = False

            elif pre_list[i].lower().startswith("updatejson"):
                # 更新json字段的值
                # noinspection PyBroadException
                try:
                    each_pre = pre_list[i].split("|", 3)
                    json_obj = replace_global_var(each_pre[1])
                    key = each_pre[2]
                    value = each_pre[3]
                    log.info("key: {}".format(key))
                    log.info("value: {}".format(value))
                    log.info("开始更新json：{0}".format(json_obj))
                    json_obj = update_json(json_obj, {key: value})
                    log.info("更新json成功，更新后为：{}".format(json_obj))
                    set_global_var(str(each_pre[1])[2:-1], json_obj, False)
                    run_flag = True
                except Exception as e:
                    log.error("json更新异常")
                    saveCode("json更新异常: {0}".format(str(e)))
                    run_flag = False

            elif pre_list[i].startswith("wait"):
                # 等待
                each_pre = pre_list[i].split('|')
                wait_time = int(each_pre[1])
                log.info("等待{}秒".format(wait_time))
                sleep(wait_time)
                run_flag = True

            elif pre_list[i].startswith(get_global_var("Database")):
                """
                pre_list[i]: ${Database}.main|select 1 from dual|var|continue
                :var： 将sql查询结果赋值给变量var
                :continue：sql执行报错时继续执行后面的语句，否则报错退出
                """
                this_pre_action = pre_list[i]
                each_pre = this_pre_action.split('|')
                # 数据库操作
                db = get_global_var("Database")
                if db_config.get(db) is None:
                    raise KeyError("db.ini未配置对应数据库信息，请检查")

                # 如果db.ini已配置数据库信息
                schema = str(each_pre[0])[len(db)+1:]
                sql = each_pre[1]
                # 替换变量
                sql = replace_global_var(sql)
                # 根据数据类型，pg数据库自动替换uuid()为gen_random_uuid()
                db_type = db_config.get(db).get("type")
                if db_type == "postgres":
                    sql = sql.replace("uuid()", "gen_random_uuid()")
                    sql = sql.replace("UUID()", "gen_random_uuid()")
                if db_type == "oracle":
                    sql = sql.replace("uuid()", "sys_guid()")
                    sql = sql.replace("UUID()", "sys_guid()")
                    sql = sql.replace("now()", "sysdate")
                log.info("{0}【{1}】执行sql语句：{2}".format(db, schema_config.get(db).get(schema), sql))
                sql_util = SQLUtil(db=db, schema=schema)
                try:
                    if sql.find("select") == 0 or sql.find("SELECT") == 0:      # 查询
                        sql_result = sql_util.select(sql)
                    else:   # 修改或删除
                        if len(each_pre) > 3 and each_pre[3].lower() == "continue":
                            skip = True
                        else:
                            skip = False
                        sql_result = sql_util.update(sql, skip=skip)
                    log.info("成功执行sql语句：{}".format(sql))
                    # 将第3个参数加入全局变量字典
                    if len(each_pre) > 2:
                        if isinstance(sql_result, int):
                            sql_result = str(sql_result)
                        if isinstance(sql_result, str):
                            set_global_var(each_pre[2], sql_result, False)
                            log.info("给变量{0}赋值：{1}".format(each_pre[2], sql_result))
                    run_flag = True
                except Exception as e:
                    if len(each_pre) > 3 and each_pre[3].lower() == "continue":
                        # 报错继续执行下一条
                        log.info("sql执行报错，忽略错误")
                        run_flag = True
                        continue
                    saveCode("执行数据库操作异常: {0}".format(str(e)))
                    run_flag = False

            else:
                each_pre = pre_list[i].split('|')
                try:
                    # 对特定数据库做操作
                    db_tmp = each_pre[0].split(".", 2)
                    db = db_tmp[0] + '.' + db_tmp[1]
                    schema = db_tmp[2]
                    if db_config.get(db) is None:
                        raise AssertionError("找不到指定数据源配置: {0}".format(db))

                    sql = each_pre[1]
                    # 替换变量
                    sql = replace_global_var(sql)
                    log.info("{0}【{1}】执行sql语句：{2}".format(db, schema_config.get(db).get(schema), sql))
                    sql_util = SQLUtil(db=db, schema=schema)
                    if sql.find("select") == 0 or sql.find("SELECT") == 0:  # 查询
                        sql_result = sql_util.select(sql)
                    else:  # 修改或删除
                        sql_result = sql_util.update(sql)
                    log.info("成功执行sql语句：{}".format(sql))
                    # 将第3个参数加入全局变量字典
                    if len(each_pre) > 2:
                        if isinstance(sql_result, int):
                            sql_result = str(sql_result)
                        if isinstance(sql_result, str):
                            set_global_var(each_pre[2], sql_result, False)
                            log.info("给变量{0}赋值：{1}".format(each_pre[2], sql_result))
                    run_flag = True
                except Exception as e:
                    if len(each_pre) > 3 and each_pre[3].lower() == "continue":
                        # 报错继续执行下一条
                        log.info("sql执行报错，忽略错误")
                        run_flag = True
                        continue
                    log.error("不支持的预置操作: {0}".format(each_pre[0]))
                    saveCode("预置条件输入错误: {0}".format(str(e)))
                    run_flag = False

            if not run_flag:  # 预置条件执行失败，会执行到空行，结束执行预置条件
                break

        log.info("预置条件全部执行完成")
    set_global_var("EndTime", datetime.now().strftime('%Y%m%d%H%M%S'), False)
    sleep(1)
    return run_flag
