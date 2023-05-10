class SWOOPCacheError(Exception):
    pass


class ConfigError(ValueError, SWOOPCacheError):
    pass


class ParsingError(ConfigError):
    pass
