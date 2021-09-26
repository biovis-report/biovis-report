# coding: utf-8
import os
import toml
import logging
from threading import local
from biovis_report import exceptions

logger = logging.getLogger(__name__)
g = local()


# Convert nested Python dict to object?
# For more details: https://stackoverflow.com/a/1305663
class Section:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class ReportConfig:
    conf_dir = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, config_file):
        self.logger = logging.getLogger('biovis-report.config.Config')
        config_file = os.path.abspath(config_file)
        try:
            self.parsed_toml = toml.load(config_file)
            if not self.parsed_toml:
                raise Exception('%s is empty.' % config_file)
        except Exception as err:
            self.logger.error("%s is not a valid toml file." % config_file)
            self.logger.error("\tError: %s" % str(err))

        schema_dir = os.path.join(self.conf_dir, 'schemas')
        self.schemas = self._load_schemas(schema_dir)
        self.logger.debug("Load schema files: %s" % str(self.schemas))

    def _check_schema(self, data, name):
        """Check the data whether satisfy the specified schema file.

        :param: data: a dict.
        :type: dict
        :param: name: schema index.
        :type: str
        """
        import json
        from jsonschema import validate
        from biovis_report.config.schema import BioVisValidator

        valid_name = 'config_%s.json' % name
        fname_lst = [x for x in self.schemas if x == valid_name or valid_name in x]
        self.logger.debug('Matched %s-th schema file: %s' % (len(fname_lst), fname_lst))
        # May be it will cause error when matched file are greater than two.
        filename = fname_lst[0] if len(fname_lst) > 0 else None
        if filename:
            self.logger.debug("Validate biovis config file.")
            with open(filename, 'r') as f:
                schema = json.load(f)
                validate(data, schema, cls=BioVisValidator)
        else:
            raise exceptions.NoSuchSchema("No such schema file: %s" % valid_name)

    def _load_schemas(self, schema_dir, abspath=True):
        """Get all schema files from the schema_dir.
        """
        # Using listdir realpath abspath with symbolic links.
        # For more details: https://stackoverflow.com/a/27156824
        if abspath:
            return [os.path.join(schema_dir, fname)
                    for fname in os.listdir(schema_dir)]
        else:
            return os.listdir(schema_dir)

    def get_section(self, section_name, is_dict=False):
        section_dict = self.parsed_toml.get(section_name)
        self._check_schema(section_dict, name=section_name)

        if is_dict:
            return section_dict
        else:
            return Section(**section_dict)


def init_config(config_file=None):
    """Initialize config object.
    """
    try:
        global g
        g.config = ReportConfig(config_file)
    except exceptions.NoConfigFile:
        pass


def get_global_config():
    global g
    if hasattr(g, 'config'):
        return g.config
    else:
        # global_config must be set properly.
        raise exceptions.NoProperConfig('To access `g.config`, '
                                        'you need to call `init_config` firstly.')
