import time


def delay_method_decorator(method_to_decorate, delay=5):
    def wrapper(self, *args, **kwargs):
        print(
            f'[delay_method_decorator] Delay "{method_to_decorate.__name__}" execution by {delay}sec'
        )
        time.sleep(delay)
        return method_to_decorate(self, *args, **kwargs)

    return wrapper
