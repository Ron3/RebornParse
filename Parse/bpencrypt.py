#coding=utf-8
"""
Created on 2013-1-31

@author: Ron2
"""


from Crypto.Cipher import AES
import json


class BPAES(object):
    """
    此模块用于加密和解密数据包.目前采用的加密算法是AES 128位加解密算法
    """

    # AES_MODE = AES.MODE_CBC
    AES_MODE = AES.MODE_ECB

    '''加密密key'''
    AES_KEY = "0123456789123456"

    @staticmethod
    def aes128_decrypt(cipherData):
        """
        AES解密
        :param cipherData           密文
        :return:
        """
        aes = AES.new(BPAES.AES_KEY, BPAES.AES_MODE)
        data = aes.decrypt(cipherData)

        if isinstance(data, bytes) == True:
            data = data.decode("utf-8")

        rawDataLength = len(data)
        paddingNum = ord(data[rawDataLength - 1])
        if paddingNum > 0 and paddingNum <= 16:
            data = data[0:(rawDataLength - paddingNum)]

        return data


    @staticmethod
    def aes128_encrypt(plainData):
        """
        AES加密
        :param plainData:           明文
        :return:
        """
        if isinstance(plainData, str) == True:
            plainData = plainData.encode("utf-8")

        size = len(plainData)
        diff = 16 - size % 16
        for i in range(diff):
            plainData += chr(diff).encode("utf-8")

        aes = AES.new(BPAES.AES_KEY, BPAES.AES_MODE)
        return aes.encrypt(plainData)


if __name__ == "__main__":
    data = {"isGM": False, "mac": "40:6C:8F:59:31:EA", "tag": 100021, "type":15002}
    data = BPAES.aes128_encrypt(json.dumps(data))
    print("data => ", data)
    print(BPAES.aes128_decrypt(data))


