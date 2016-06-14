import threading
from datetime import datetime


class CronJob(object):
    """
    This class looks for the cronjob.py file within the packages application namespace and tries to run it
    All crons do() must run a seperate thread to prevent system pausing to users. Even the entire CronJob.__init__()
    will also be a single thread
    """

    def __init__(self):

        class MainCronThread(threading.Thread):
            def __init__(self, name):
                threading.Thread.__init__(self)
                self.name = name

            def run(self):
                start = datetime.now()
                # membership cron
                from packages.membership.cronjobs import CronJob as MembershipCron
                MembershipCron().do()

                completed = (datetime.now() - start)
                msg = "%s Completed in %s seconds or %s microseconds" \
                      % (self.name, completed.seconds, completed.microseconds)
                print msg

        my_thread = MainCronThread("Main_cron_thread")

        print "We are here"

        if not my_thread.isAlive():
            my_thread.start()