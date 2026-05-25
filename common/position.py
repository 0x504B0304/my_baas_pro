module_cache = {}


def import_module(self, module_name):
    game_server = self.game_server

    cn_position = __import__(f'assets.position.cn.{module_name}', fromlist=['x']).x.copy()

    if game_server == 'cn':
        return cn_position

    try:
        cu_position = __import__(f'assets.position.{game_server}.{module_name}', fromlist=['x']).x
        return {**cn_position, **cu_position}
    except ImportError:
        return cn_position


def get_box(self, name):
    module, name = name.rsplit('_', 1)
    key = '{0}_{1}'.format(self.game_server, module)
    if key not in module_cache:
        module_cache[key] = import_module(self, module)
    return module_cache[key][name]
