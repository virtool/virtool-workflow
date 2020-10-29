import inspect


def _extract_params(func):
    parameters = inspect.signature(func).parameters
    return list(parameters.values())


def hook(func):
    params = _extract_params(func)
    func._callbacks = []

    def _callback(callback):
        callback_params = _extract_params(callback)
        if len(callback_params) != len(params):
            raise ValueError("Invalid number of parameters")
        for hook_param, callback_param in zip(params, callback_params):
            if hook_param.annotation is inspect.Parameter.empty:
                continue
            if callback_param.annotation is inspect.Parameter.empty:
                continue
            if hook_param.annotation != callback_param.annotation:
                raise ValueError("Invalid parameters")
        func._callbacks.append(callback)

    func.callback = _callback
    return func


@hook
def on_error(string: str):
    pass


@on_error.callback
def callback(item: int):
    pass


