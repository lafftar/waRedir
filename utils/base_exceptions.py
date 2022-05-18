
# @todo - log these errors to discord.


class BadTaskSettings(Exception):
    pass

class AccNotRegistered(Exception):
    pass

class LoginTimeout(Exception):
    pass

class FailedLogin(Exception):
    pass

class AkamaiGenTimeout(Exception):
    pass

class ReqFailed(Exception):
    pass

class RestartWS(Exception):
    pass

class CouldNotGet2CapBalance(Exception):
    pass

class CouldNotGetWorkingProxy(Exception):
    pass

class UnsupportedSystem(Exception):
    pass

class NoProxiesLoaded(Exception):
    pass
