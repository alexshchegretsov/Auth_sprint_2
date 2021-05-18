class DeviceType:
    WEB = 'web'
    SMART = 'smart'
    MOBILE = 'mobile'

    __slots__ = []

    @classmethod
    def as_list(cls):
        return [cls.WEB, cls.SMART, cls.MOBILE]
