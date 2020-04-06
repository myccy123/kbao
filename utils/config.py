import configparser


class Configer(configparser.ConfigParser):
    def to_dict(self):
        print(self._sections)
        d = dict(self._sections)
        for k in d:
            d[k] = dict(d[k])
        return d


def get_conf(config_file=r'conf\api.ini'):
    config = Configer()
    config.read(config_file, encoding="utf-8-sig")
    return config.to_dict()
