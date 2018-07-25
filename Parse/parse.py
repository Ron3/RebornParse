#coding=utf-8
"""
Create On 2018/5/26

@author: Ron2
"""

import os
import gc
# import bson
import json
import xlrd
import types
import traceback



class Parse(object):
    """
    解释Excel表格,将其数据转成对应的bson
    注意事项:  所有的sheet表名都要英文
    多国语言这样写: 说明-中, 说明-英(跟暴2一样)
    """
    def __init__(self, parseSettingDic):
        """
        """
        self.excelSuffix = ".xls"
        self.excelSuffix2 = ".xlsx"
        self.saveFileSuffix = ".dat"                # 保存的格式后缀

        self.excelPath = ""                         # excel表格的路径
        self.outputPath = ""                        # 保存解出来的

        self.excelFileNameArray = []                # excel表格的全路径
        self.parseSettingDic = parseSettingDic      # {"-中": "CN"}


    def _initPath(self):
        """
        初始化excel
        :return: 
        """
        # self.excelPath = os.path.abspath(os.path.join(os.getcwd(), "../"))
        # print u"excel数据路径 ===> ", self.excelPath


    def _fileAllExcelFile(self):
        """
        遍历所有的excel文件.这里不会遍历子目录
        :return: 
        """
        dirArray = os.walk(self.excelPath)
        for root, dirs, files in dirArray:
            for fileName in files:
                if fileName.startswith("~$") == True:
                    continue

                fullPath = os.path.join(root, fileName)
                if fullPath.endswith(self.excelSuffix) == True or fullPath.endswith(self.excelSuffix2) == True:
                    self.excelFileNameArray.append(fullPath)
                    print u"需要解析的excel ===> ", fileName

        print u"一共需要解释 ===> ", len(self.excelFileNameArray)


    def _getTitleArray(self, tableObj):
        """
        得到标题数组
        :return: 
        """
        titleArray = []
        tmpArray = tableObj.row_values(0)
        for title in tmpArray:
            title = title.strip()  # 只要遇到第一个空字符串就推出
            if len(title) <= 0:
                break

            titleArray.append(title.strip())

        return titleArray


    def _getTitleArrayForNormal(self, tableObj):
        """
        获取普通标题头的(排除哪些多国语言相关的)
        :return: 
        """
        resultArray = []
        titleArray = self._getTitleArray(tableObj)
        for title in titleArray:
            if self._isTitleInMultiLan(title) == False:
                resultArray.append(title)

        return resultArray


    def _getTitleArrayForMultiLan(self, tableObj):
        """
        获取多国语言的标题头
        :param tableObj: 
        :return: 
        """
        resultArray = []
        titleArray = self._getTitleArray(tableObj)
        for title in titleArray:
            if self._isTitleInMultiLan(title) == True:
                resultArray.append(title)

        return resultArray


    def _isTitleInMultiLan(self, title):
        """
        判定这个列名.是否是多国语言版
        :return: 
        """
        if title == None or len(title) <= 0:
            return False

        for suffix in self.parseSettingDic.keys():
            if title.endswith(suffix) == True:
                return True

        return False


    def _parseExcel(self):
        """
        解析excel.不做任何异常保护.如果最后没成功.则让大家知道结果
        :return: 
        """
        for fullPath in self.excelFileNameArray:
            gc.collect()

            excelDataObj = xlrd.open_workbook(fullPath)
            sheetNameArray = excelDataObj.sheet_names()
            for sheetName in sheetNameArray:
                sheetObj = excelDataObj.sheet_by_name(sheetName)
                resultArray = self._parseSheet(sheetObj)
                self._writeToFile(resultArray, sheetObj)

                del sheetObj
                del resultArray

            del excelDataObj
            del sheetNameArray


    def _parseSheet(self, sheetObj):
        """
        解释一张表
        :param sheetObj: 
        :return: 
        """
        ''' 1, 找出 '''
        allTitleArray = self._getTitleArray(sheetObj)
        normalTitleArray = self._getTitleArrayForNormal(sheetObj)
        multiLanTitleArray = self._getTitleArrayForMultiLan(sheetObj)

        # print "allTitleArray ==> ", json.dumps(allTitleArray)
        # print "normalTitleArray ==> ", json.dumps(normalTitleArray)
        # print "multiLanTitleArray ==> ", json.dumps(multiLanTitleArray)

        ''' 3, 开始解表 '''
        resultArray = []
        for rowIndex in range(sheetObj.nrows):
            if rowIndex == 0:                   # 第一行是标题
                continue

            valueArray = sheetObj.row(rowIndex)

            ''' 如果第一列的值为空, 后继直接continue '''
            if len(valueArray) > 0:
                tmpCell = valueArray[0]
                tmpValue = tmpCell.value
                if tmpCell.ctype == xlrd.XL_CELL_EMPTY or tmpCell.ctype == xlrd.XL_CELL_BLANK or (isinstance(tmpValue, str) and len(tmpValue.strip()) <= 0):
                    continue

            dic = {}
            for tmpIndex, title in enumerate(allTitleArray):
                valCell = valueArray[tmpIndex]
                value = valCell.value

                ''' 过滤空白字符 '''
                if valCell.ctype != xlrd.XL_CELL_EMPTY and valCell.ctype != xlrd.XL_CELL_BLANK or (isinstance(tmpValue, str) and len(tmpValue.strip()) <= 0):
                    if isinstance(value, str) and len(value.strip()) <= 0:
                        valCell.ctype = xlrd.XL_CELL_EMPTY

                ''' 如果不是空的.就放进去 '''
                if valCell.ctype != xlrd.XL_CELL_EMPTY and valCell.ctype != xlrd.XL_CELL_BLANK:
                    dic[title] = value
                else:
                    dic[title] = None

            resultArray.append(dic)
        return resultArray


    def _writeToFile(self, resultArray, sheetObj):
        """
        写入文件.并且这里处理多国语言
        :param resultArray: 
        :param sheetObj: 
        :return: 
        """
        normalTitleArray = self._getTitleArrayForNormal(sheetObj)
        multiTitleArray = self._getTitleArrayForMultiLan(sheetObj)

        multiLanDataDic = {}  # {EN: [{第一条数据}, {第二条数据}]}
        for lan in self.parseSettingDic.values():
            multiLanDataDic[lan] = []

        for rowDic in resultArray:
            totalLanDataDic = {}                            # 多国语言版本的数据抽出来放在这里
            for title in multiTitleArray:
                v = rowDic.pop(title)
                totalLanDataDic[title] = v

            ''' 每一种语言.需要一个dic.每一个dic是对应一行的数据{"说明-中": "", "名字-中": ""}.其实那个后缀语言是不会有的.只是示例用 '''
            everyRowLanDic = {}
            for lan in self.parseSettingDic.values():
                everyRowLanDic[lan] = {}

            for title, value in totalLanDataDic.items():
                lan = self._getEnumLanByTitle(title)        # 得到语言枚举
                rowLanDic = everyRowLanDic.get(lan)         # 得到这一行这一种语言的dic
                if rowLanDic == None:
                    exit(1)

                rowLanDic[self._getTitleWithNotSuffix(title)] = value
                # print "Ron => ", self._getTitleWithNotSuffix(title), value
                # print("rowLanDic===> ", rowLanDic)

            ''' 然后在把每一种语言放进去对应的数组 '''
            for lan, rowLanDic in everyRowLanDic.items():
                rowLanArray = multiLanDataDic.get(lan)
                if rowLanArray == None:
                    exit(1)

                rowLanArray.append(rowLanDic)

        for lan, ronLanArray in multiLanDataDic.items():
            # data = bson.dumps({"dataArray": ronLanArray})
            # data = json.dumps({"dataArray": resultArray})
            data = json.dumps(ronLanArray)
            fullPath = self._getSaveFileFullPath(sheetObj.name, lan)
            fileObj = open(fullPath, "wb")
            fileObj.write(data.encode("utf-8"))
            fileObj.close()
            del data

        del multiLanDataDic

        # data = bson.dumps({"dataArray": resultArray})
        # data = json.dumps({"dataArray": resultArray})
        data = json.dumps(resultArray)
        fullPath = self._getSaveFileFullPath(sheetObj.name)
        fileObj = open(fullPath, "wb")
        fileObj.write(data.encode("utf-8"))
        fileObj.close()
        del data


    def _getSaveFileFullPath(self, sheetName, lan=None):
        """
        获取保存的名字.
        :param sheetName:
        :param lan:                 多国语言的语言
        :return: 
        """
        # path = os.path.join(self.excelPath, "output")
        path = self.outputPath

        if lan == None:
            return os.path.join(path, sheetName + self.saveFileSuffix)

        return os.path.join(path, sheetName + "_" + lan + self.saveFileSuffix)


    def _getEnumLanByTitle(self, title):
        """
        根据title得知这个语言对应的枚举
        :param title: 
        :return:            EN, CN之类的
        """
        if title == None:
            return None

        for suffix, lan in self.parseSettingDic.items():
            if title.endswith(suffix) == True:
                return lan

        return None


    def _getTitleWithNotSuffix(self, title):
        """
        获取标题是没有后缀的.
        :param title:               说明-中
        :return:                    说明
        """
        return title[0: -2]


    def _initConfigJson(self):
        """
        初始化Json
        :return: 
        """
        try:
            fileObj = open("./Config.json", "rb")
            data = fileObj.read()
            dataDic = json.loads(data)
            fileObj.close()

            self.excelPath = dataDic.get("DataPath")
            self.outputPath = dataDic.get("OutPutPath")
        except:
            traceback.print_exc()
            exit(1)

        print u"excel数据路径 ==> ", self.excelPath
        print u"输出路径 ==> ", self.outputPath

        try:
            os.makedirs(self.outputPath)
        except:
            pass


    def start(self):
        """
        开始解析
        :return: 
        """
        self._initConfigJson()

        self._initPath()
        self._fileAllExcelFile()
        self._parseExcel()
        print("解表成功.........")





if __name__ == "__main__":
    PARSE_SETTING_DIC = {}
    PARSE_SETTING_DIC[u"-中"] = "cn"
    PARSE_SETTING_DIC[u"-繁"] = "tc"
    PARSE_SETTING_DIC[u"-英"] = "en"
    PARSE_SETTING_DIC[u"-日"] = "jp"
    PARSE_SETTING_DIC[u"-韩"] = "ko"
    PARSE_SETTING_DIC[u"-法"] = "fr"
    PARSE_SETTING_DIC[u"-德"] = "de"
    PARSE_SETTING_DIC[u"-泰"] = "th"
    PARSE_SETTING_DIC[u"-葡"] = "pt"
    PARSE_SETTING_DIC[u"-俄"] = "ru"
    PARSE_SETTING_DIC[u"-西"] = "es"

    obj = Parse(PARSE_SETTING_DIC)
    obj.start()


