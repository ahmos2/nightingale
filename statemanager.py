import redis
class StateManager(object):
    def __init__(self):
        self.redis=redis.Redis()
    def get(self,instanceName, key):
        return self.redis.get(instanceName+"."+key)
    def set(self,instanceName, key, value):
        self.redis.set(instanceName+"."+key, value)
    def UniqueName(self,company,ship,controller,instance):
        return company+":"+ship+":"+controller+":"+instance
