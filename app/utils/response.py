from flask import request, current_app

from app.utils.code import ResponseCode, ResponseMessage


class ResMsg(object):
    """
    封装响应文本
    """

    def __init__(self, data=None, code=ResponseCode.Success, rq=request):
        # 获取请求中语言选择,默认为中文
        self._data = data
        self._msg = ResponseMessage.Success.value
        self._code = code.value

    def update(self, code=None, data=None, msg=None):
        """
        更新默认响应文本
        :param code:响应编码
        :param data: 响应数据
        :param msg: 响应消息
        :return:
        """
        if code is not None:
            self._code = code.value
            self._msg = ResponseMessage[code.name].value

        if data is not None:
            self._data = data
        if msg is not None:
            self._msg = msg

    def put(self, name=None, value=None):
        """
        在响应文本中加入新的字段，方便使用
        :param name: 变量名
        :param value: 变量值
        :return:
        """
        if name is not None and value is not None:
            self.__dict__[name] = value

    @property
    def data(self):
        """
        输出响应文本内容
        :return:
        """
        body = self.__dict__
        body["msg"] = body.pop("_msg")
        body["code"] = body.pop("_code")
        body["data"] = body.pop("_data")
        if not body["data"]:
            del body["data"]
        return body
