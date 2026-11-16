class AxinstallScreen:
    def __init__(self, set_valid):
        super().__init__()
        self._set_valid = set_valid

        self.valid = False

    def is_valid(self):
        return self.valid

    def set_valid(self, valid: bool):
        self.valid = valid
        if hasattr(self, "window") and getattr(self.window, "current_page", None) is not None:
            if self.window.current_page == self:
                self._set_valid(valid)
        else:
            self._set_valid(valid)

    def on_show(self):
        pass

    def on_complete(self):
        pass
