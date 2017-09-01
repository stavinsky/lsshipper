from .structure import structure
import configparser
from .validator import ConfigValidator
import pprint


originga_config = configparser.ConfigParser(interpolation=None)
originga_config.read("config.ini")
validator = ConfigValidator(originga_config, structure)

config = validator.validate_all_fields()
__all__ = ['config']

if __name__ == "__main__":
    pprint.pprint(config['files']['pattern'])
