class Result(object):
    STATUS_ERROR = "error"
    STATUS_SUCCESS = "success"
    _default_code = 500

    def __init__(self, status, code=_default_code, data={}, msg=""):
        self._status = status
        self._code = code
        self._data = data
        self._msg = msg

    def status(self):
        return self._status

    def code(self):
        return self._code

    def data(self):
        return self._data

    def msg(self):
        return self._msg

    def setData(self, obj):
        self._data = obj

    def json(self):
        return { "status": self._status, "code": self._code }


class Error(Result):
    def __init__(self, code, msg):
        super(Error, self).__init__(status=Result.STATUS_ERROR, code=code, msg=msg)

    def json(self):
        return { "status": self._status, "code": self._code, "msg": self._msg }

class Success(Result):
    def __init__(self, data):
        super(Success, self).__init__(status=Result.STATUS_SUCCESS, code=200, data=data)

    def json(self):
        return { "status": self._status, "code": self._code, "data": self._data }
