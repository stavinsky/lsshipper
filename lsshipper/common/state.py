class State:
    def __init__(self, loop, need_shutdown=False, ):
        self._need_shutdown = need_shutdown
        self.loop = loop

    @property
    def need_shutdown(self):
        return self._need_shutdown

    def shutdown(self):
        self._need_shutdown = True

    def __repr__(self,):
        return "shutdown is{} needed".format(
            "" if self._need_shutdown else " not")
