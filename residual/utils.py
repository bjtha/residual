class ExtendableUrl:

    def __init__(self, __base_url: str, /):
        self._url = __base_url

    def __truediv__(self, other):
        return ExtendableUrl('/'.join([self._url, str(other)]))

    def __repr__(self):
        return self._url
