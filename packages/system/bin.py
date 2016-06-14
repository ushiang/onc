
from packages.bin.middleware.syslicense import SysLicense


# path to member photo upload
def path_and_rename(instance, filename):
    import os
    import hashlib
    import datetime
    print SysLicense.lid, "hello"
    ext = '.' + filename.split('.')[-1]
    filename = hashlib.md5(instance.lid + instance.sys + str(datetime.datetime.now())).hexdigest() + ext
    return os.path.join('license/%s' % instance.lid, filename)
