# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import os
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Plugin(Base):
    __tablename__ = 'plugin'
    id = Column(String(60), primary_key=True)
    name = Column(String(250), nullable=False)
    command = Column(String(255), nullable=False)
    command_md5 = Column(String(64), nullable=False)
    is_docker = Column(Boolean, nullable=False)
    container_id = Column(String(64), nullable=True)
    process_id = Column(String(8), nullable=True)
    status = Column(String(30), nullable=False)


def init_db(site_dir):
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///%s' % os.path.join(site_dir, 'plugin.db'))

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)
