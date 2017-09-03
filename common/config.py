from configobj import ConfigObj
import logging
import configobj
import re
import sys
import os
import ast
from docopt import docopt
logger = logging.getLogger("general")

opt_config = """
Usage:
    main.py [--config=<config.ini>]
"""

args = docopt(opt_config, version='Naval Fate 2.0')

config_file = 'config.ini'
if args['--config']:
    config_file = args['--config']
if not all((os.path.exists(config_file), os.path.isfile(config_file))):
    print('Config file not found')
    sys.exit(1)


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
