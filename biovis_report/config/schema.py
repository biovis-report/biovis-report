# -*- coding: utf-8 -*-
"""
    report.schema
    ~~~~~~~~~~~~~~~~~~~~

    Custom schema validator for biovis config.

    :copyright: © 2019 by the BioVis team.
    :license: AGPL, see LICENSE.md for more details.
"""

from jsonschema.exceptions import ValidationError
from jsonschema import validators, Draft7Validator


all_validators = dict(Draft7Validator.VALIDATORS)

BioVisValidator = validators.create(
    meta_schema=Draft7Validator.META_SCHEMA, validators=all_validators
)
