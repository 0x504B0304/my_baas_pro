from modules.baas import home


def start(self):
    home.go_home(self)
    to_group(self)
    home.go_home(self)


def to_group(self):
    pos = {
        'home_student': (535, 640),
        'group_guide': (310, 377),
        'group_sign-up-confirm': (644, 491),
    }
    home.to_menu(self, 'group_menu', pos)
