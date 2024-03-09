class ContextReference(object):

    def __get__(self, instance, owner):
        return instance._context

    def __set__(self, instance, value):
        raise AttributeError(f"Can't modify context attribute!")
