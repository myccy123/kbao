import redis


def get_redis_cli(host='127.0.0.1', port=6379, password='kb1234@1234'):
    return redis.Redis(host=host, port=int(port), password=password, decode_responses=True)


class MyRedis:

    def __init__(self, cli):
        self.cli = cli

    @classmethod
    def connect(cls, host='127.0.0.1', port=6379, password='kb1234@1234'):
        cli = redis.Redis(host=host, port=int(port), password=password, decode_responses=True)
        return cls(cli)

    def incr(self, key, amount=1, limit=None):
        val = self.cli.get(key)
        if val is None:
            self.cli.set(key, 0)

        if limit is not None and int(self.cli.get(key)) >= limit:
            self.cli.set(key, 0)
        val = self.cli.incr(key, amount)
        self.cli.close()
        return val

    def set(self, key, value, expire=None):
        self.cli.set(key, value)
        if expire is not None:
            self.cli.set(key, expire)
        self.cli.close()

    def get(self, key):
        val = self.cli.get(key)
        self.cli.close()
        return val

    def hset(self, name, key, value):
        self.cli.hset(key, name, value)
        self.cli.close()

    def hget(self, name, key):
        val = self.cli.hget(name, key)
        self.cli.close()
        return val
