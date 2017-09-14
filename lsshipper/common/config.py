from configobj import ConfigObj
import logging
import configobj
import sys
import ast
import os
import argparse


logger = logging.getLogger("general")


def prepare_config():
    parser = argparse.ArgumentParser(description='Logstash file shipper')
    parser.add_argument('--config_dir', default='.',
                        help='path to config directory')
    parser.add_argument('--run-once', default=False, type=bool,
                        help='Upload files one by one without watching')
    args = parser.parse_args()
    config_dir = os.path.abspath(args.config_dir)

    log_config_file = os.path.join(config_dir, 'log_config.ini')
    config_file = os.path.join(config_dir, 'config.ini')
    logging.config.fileConfig(log_config_file)

    try:
        _config = ConfigObj(config_file, raise_errors=True)
    except (configobj.ParseError, configobj.UnreprError) as e:
        logger.error(e)
        sys.exit(1)

    config = _config.dict()
    config['files']['pattern'] = ast.literal_eval(config['files']['pattern'])
    config['files']['newline'] = ast.literal_eval(config['files']['newline'])

    config['files']['newline'] = config['files']['newline'].encode()

    config['ssl']['enable'] = _config['ssl'].as_bool('enable')
    config['general'] = {}
    config['general']['run-once'] = args.run_once
    return config
