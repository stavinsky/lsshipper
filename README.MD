### Description

This is very simple replacement of ElasticSearch filebeat.

### Usage

#### install

```bash
pip install git+https://github.com/stavinsky/lsshipper
```
after that create config directory anywhere you want and put 2 config files there.

1. log_config.ini - this is config for logging system.
[example with verbose logs](../blob/master/example_config_folder/log_config.ini)
2. config.ini - main config. Make sure that `pattern` and `newline` parameters is doublequotted.
[example with verbose logs](../blob/master/example_config_folder/config.ini)
