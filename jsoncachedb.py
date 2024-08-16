import os
import json

class filedb:
    def __init__(self, datafile, datapath, autocreation = False):
        self.datafile = os.path.join(datapath, datafile)
        if autocreation and not os.path.isfile(self.datafile):
            with open(self.datafile, "w") as f:
                f.write("{}")
                f.close()
    
    def load(self):
        with open(self.datafile, "r") as f:
            return json.loads(f.read())
    
    def save(self, data):
        with open(self.datafile, "w") as f:
            f.write(json.dumps(data))

class CACHE:
    CACHEHIT = 1
    CACHEMISS = 0
    SUCCESS = True

class jsondb(filedb):
    def __init__(self, cid):
        memfile = "jsondb_%s.json" % cid
        super().__init__(memfile, autocreation=True, datapath="runinfo")
        self.cache = self.load()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        pass

    def get_cache(self, did):
        if did in self.cache:
            return CACHE.CACHEHIT, self.cache[did]
        return CACHE.CACHEMISS, ""
    
    def store_cache(self, did, data):
        self.cache[did] = data
        self.save(self.cache)
        return CACHE.SUCCESS
    
    def delete_cache(self, did):
        del self.cache[did]
        self.save(self.cache)
