[![PyPI version](https://badge.fury.io/py/lsshipper.svg)](https://badge.fury.io/py/lsshipper)
### Description

This is very simple replacement for ElasticSearch filebeat.

### Usage

#### install

```bash
pip install git+https://github.com/stavinsky/lsshipper
```
after that create config directory anywhere you want and put 2 config files there.

1. log_config.ini - this is config for logging system.
[example with verbose logs](../master/example_config_folder/log_config.ini)
2. config.ini - main config. Make sure that `pattern` and `newline` parameters is doublequotted.
[example with verbose logs](../master/example_config_folder/config.ini)


#### running

It can be started as a module:
```bash
python -m lsshipper --config_dir <dir with configs>
```


### Why?

There is windows software that adds preallocated block of zeroes(\\x00) to log file. Original filebeat skips such blocks. So big part of logs can be lost.

### Speed

On my mac mini late 2003 it can write to network about 2Mb/s. I will test later on windows and linux. I believe on linux it should be much faster.


### Problems
1. On very fast server reconnects it can loose one log string. Please check test_connection.py
