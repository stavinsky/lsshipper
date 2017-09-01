import ast
import re


class ValidationError(Exception):
    pass


class ConfigValidator:
    validators = {}

    @classmethod
    def register_validator(cls, name, validator):
        cls.validators[name] = validator

    def __init__(self, config, structure):
        self.config = config
        self.structure = structure

    def validate_sections(self):
        for section in self.structure.keys():
            if section not in self.config.sections():
                raise Exception("Section {} missed in config".format(section))
            for key in self.structure[section].keys():
                if key not in self.config[section].keys():
                    raise Exception(
                        "{} missed in section {}".format(key, section))

        return True

    def validate_value(self, value, validator_name):
        return self.validators[validator_name](value)

    def validate_all_fields(self):
        v_conf = dict()  # validated config
        error = False
        for sec in self.structure.keys():
            v_conf[sec] = {}
            # print(type(self.structure[sec].items()))
            for name, val in self.structure[sec].items():
                new_val, error = self.validate_value(
                    self.config[sec][name], val)
                if error:
                    raise ValidationError(
                        "{} in {} -> {}".format(error, sec, name))
                v_conf[sec][name] = new_val
        return v_conf


def to_str(val):
    new_val = val
    error = False
    try:
        if re.match(r"^([\"\']|\"\"\").*\1$", val):
            new_val = ast.literal_eval(val)
    except ValueError:
        error = "Can't convert to str"
    return new_val, error


def to_int(val):
    new_val = None
    error = False
    try:
        new_val = int(val)
    except ValueError:
        error = "Can't convert to int"
    return new_val, error


def to_bool(val):
    new_val = None
    error = "Can't convert to bool"

    if val in ("yes", "True", "true", ):
        error = False
        new_val = True
    if val in ("no", "False", "false", ):
        error = False
        new_val = False
    return new_val, error


def to_path(val):
    import os
    new_val = os.path.abspath(val)
    error = False
    if not os.path.exists(os.path.abspath(val)):
        error = "File {} doesn't exists".format(new_val)
        new_val = None
    return new_val, error


def to_loglevel(val):
    import logging
    error = False
    new_val = val.upper()
    new_val = logging.getLevelName(new_val)
    if not isinstance(new_val, int):
        error = "Log Level can be: INFO, DEBUG,...,ERROR"
        new_val = None
    return new_val, error


def to_regexp(val):
    val, error = to_str(val)
    try:
        new_val = re.compile(val)
        error = False
    except re.error:
        new_val = None
        error = "cant compile regular expression {}".format(val)
    return new_val, error


ConfigValidator.register_validator("str", to_str)
ConfigValidator.register_validator("int", to_int)
ConfigValidator.register_validator("bool", to_bool)
ConfigValidator.register_validator("path", to_path)
ConfigValidator.register_validator("log_level", to_loglevel)
ConfigValidator.register_validator("re", to_regexp)
