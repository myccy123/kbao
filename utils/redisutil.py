import redis


def get_redis_cli(host='127.0.0.1', port=6379):
    return redis.Redis(host=host, port=int(port), decode_responses=True)


class MyRedis:

    def __init__(self, cli):
        self.cli = cli

    @classmethod
    def connect(cls, host='127.0.0.1', port=6379):
        cli = redis.Redis(host=host, port=int(port), decode_responses=True)
        return cls(cli)

    def incr(self, key, amount=1, limit=None):
        val = self.cli.get(key)
        if val is None:
            self.set(key, 0)

        if limit is not None and int(self.cli.get(key)) >= limit:
            self.cli.set(key, 0)
        val = self.cli.incr(key, amount)
        self.cli.close()
        return val
