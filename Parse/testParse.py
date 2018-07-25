#coding=utf-8
"""
Create On 2018/5/28

@author: Ron2
"""

import bson
import json


class ReadParseData(object):
    """
    测试读取读取
    """
    def __init__(self, path, parseSettingDic):
        """
        :param path: 
        """
        self.path = path
        self.parseSettingDic = parseSettingDic


    def start(self):
        """
        开始
        :return: 
        """
        fileObj = open(self.path, "rb")
        data = fileObj.read()
        fileObj.close()

        fileObj = open("../output/item_EN.dat", "rb")
        lanData = fileObj.read()
        fileObj.close()

        dataDic = bson.loads(lanData)
        lanDataArray = dataDic.get("dataArray")

        dataDic = bson.loads(data)
        dataArray = dataDic.get("dataArray")
        for index, dic in enumerate(dataArray):
            print(index+2, "   ", int(dic.get("编号")), "   ", dic.get("名字+星-索引"), lanDataArray[index].get("名称"))
            if index >= 100:
                break





if __name__ == "__main__":
    PARSE_SETTING_DIC = {}
    PARSE_SETTING_DIC[u"-中"] = "CN"
    PARSE_SETTING_DIC[u"-繁"] = "TC"
    PARSE_SETTING_DIC[u"-英"] = "EN"
    PARSE_SETTING_DIC[u"-日"] = "JP"
    PARSE_SETTING_DIC[u"-韩"] = "KO"
    PARSE_SETTING_DIC[u"-法"] = "FR"
    PARSE_SETTING_DIC[u"-德"] = "DE"
    PARSE_SETTING_DIC[u"-泰"] = "TH"
    PARSE_SETTING_DIC[u"-葡"] = "PT"
    PARSE_SETTING_DIC[u"-俄"] = "RU"
    PARSE_SETTING_DIC[u"-西"] = "ES"

    path = "../output/item.dat"
    obj = ReadParseData(path, PARSE_SETTING_DIC)
    obj.start()
