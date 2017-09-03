from configobj import ConfigObj
import logging
import configobj
import re
import sys
import ast

logger = logging.getLogger("general")

config_file = 'config.ini'

try:
    _config = ConfigObj(config_file, raise_errors=True)
except (configobj.ParseError, configobj.UnreprError) as e:
    logger.error(e)
    sys.exit(1)

config = _config.dict()
config['files']['pattern'] = ast.literal_eval(config['files']['pattern'])
config['files']['newline'] = ast.literal_eval(config['files']['newline'])

config['files']['pattern'] = re.compile(config['files']['pattern'])
config['files']['newline'] = config['files']['newline'].encode()

config['ssl']['enable'] = _config['ssl'].as_bool('enable')
