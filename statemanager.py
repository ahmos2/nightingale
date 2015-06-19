class StateManager(object):
    instanceState={}
    def get(self,instanceName, key):
        if not self.instanceState.has_key(instanceName):
            return None
        if not self.instanceState[instanceName].has_key(key):
            return None
        return self.instanceState[instanceName][key]
    def set(self,instanceName, key, value):
        if not self.instanceState.has_key(instanceName):
            self.instanceState[instanceName]={}
        self.instanceState[instanceName][key]=value
    def UniqueName(self,company,ship,controller,instance):
        return company+":"+ship+":"+controller+":"+instance
