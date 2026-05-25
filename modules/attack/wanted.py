from modules.baas import home
from modules.attack import special_entrust

x = {}

entrust_position = {
    'gjgl': (950, 200),
    'smtl': (950, 310),
    'jt': (950, 420),
}


def start(self):
    home.go_home(self)
    special_entrust.choose_entrust(self, entrust_position, 9)
    home.go_home(self)
