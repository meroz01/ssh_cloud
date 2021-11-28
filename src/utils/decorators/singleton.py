def singleton(decorated_class):
    instances = {}

    def get_instance(*args, **kwargs):
        if decorated_class not in instances:
            instances[decorated_class] = decorated_class(*args, **kwargs)
        return instances[decorated_class]

    return get_instance
