import redis
class StateManager(object):
    def __init__(self):
        self.rcon=redis.Redis()
    def get(self,instanceName, key):
        return self.rcon.get(instanceName+"."+key)
    def set(self,instanceName, key, value):
        self.rcon.set(instanceName+"."+key,value)
    def UniqueName(self,company,ship,controller,instance):
        return company+":"+ship+":"+controller+":"+instance
