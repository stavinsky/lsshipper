from configobj import ConfigObj
import logging
import configobj
import re
import sys
import ast
import os
import argparse


logger = logging.getLogger("general")


def prepare_config(config):
    parser = argparse.ArgumentParser(description='Logstash file shipper')
    parser.add_argument('--config_dir', default='.')
    args = parser.parse_args()
    config_dir = os.path.abspath(args.config_dir)
    print(config_dir)

    log_config_file = os.path.join(config_dir, 'log_config.ini')
    config_file = os.path.join(config_dir, 'config.ini')
    logging.config.fileConfig(log_config_file)

    try:
        _config = ConfigObj(config_file, raise_errors=True)
    except (configobj.ParseError, configobj.UnreprError) as e:
        logger.error(e)
        sys.exit(1)

    config.update(_config.dict())
    config['files']['pattern'] = ast.literal_eval(config['files']['pattern'])
    config['files']['newline'] = ast.literal_eval(config['files']['newline'])

    config['files']['pattern'] = re.compile(config['files']['pattern'])
    config['files']['newline'] = config['files']['newline'].encode()

    config['ssl']['enable'] = _config['ssl'].as_bool('enable')
    return config


config = {}
