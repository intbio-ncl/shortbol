from .error import ExtensionError


class And:

    def __init__(self, *sub_exts):
        self._sub_exts = sub_exts

    def run(self, triplepack,env):
        for ext in self._sub_exts:
            ext.run(triplepack)

        return triplepack


class Or:

    def __init__(self, *sub_exts):
        self._sub_exts = sub_exts

    def run(self, triplepack,env):
        for ext in self._sub_exts[:-1]:
            try:
                ext.run(triplepack)
                return triplepack
            except ExtensionError:
                pass

        self._sub_exts[-1].run(triplepack)
        return triplepack
