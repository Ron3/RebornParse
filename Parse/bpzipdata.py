#coding=utf-8
"""
Created on 2015-05-28

@author: Ron2
"""


import zlib


class BPZipData(object):
    """
    压缩数据
    """

    @staticmethod
    def zip_data(requestData, level=6):
        """
        压缩数据
        :param requestData:
        :param level:
        :return:
        """
        if isinstance(requestData, str) == True:
            requestData = requestData.encode("utf-8")

        return zlib.compress(requestData, level)


    @staticmethod
    def unzip_data(responseData):
        """
        解压缩数据
        :param responseData:
        :return:
        """
        return zlib.decompress(responseData)


if __name__=="__main__":

    # originData = "xxx xx fds dfjadksj fasdkf xx0 0 xx000000"
    originData = '''{"data": "ron"}'''

    compressData = BPZipData.zip_data(originData)
    print("compressData ==> ", len(compressData), compressData)

    decompressData = BPZipData.unzip_data(compressData)
    print("decompressData ==> ", len(decompressData), decompressData)

    fileObj = open("../output/itemgroup.dat", "rb")
    data = fileObj.read()
    fileObj.close()

    data = BPZipData.zip_data(data)

    fileObj = open("./test.dat", "wb")
    fileObj.write(data)
    fileObj.close()


