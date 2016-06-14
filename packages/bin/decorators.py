import inspect
from packages.bin.auth import Auth


def is_authenticated(func):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def check_authentication(*args, **kwargs):
        s = Auth().is_auth(*args)
        if not s:
            return Auth().do_logout(*args)

        #kwargs['whoami'] = Auth.whoami(*args)

        return func(*args, **kwargs)

    return check_authentication


def ancillary(func):
    """
    Decorator for views to check if it is an ancillary function
    or a main function. Delete functions are ancillary
    """
    def is_ancillary(*args, **kwargs):

        argspec = inspect.getargspec(func)

        try:
            index = argspec.args.index('ancillary')
            if argspec.args[index] is True:
                print "ARGSPEC"
                return func(*args, **kwargs)
            else:
                return is_ancillary
        except ValueError:
            return is_ancillary

    return is_ancillary