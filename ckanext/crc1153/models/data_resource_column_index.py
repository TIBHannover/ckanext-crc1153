# encoding: utf-8

from sqlalchemy import Column, ForeignKey, orm
from sqlalchemy import types as _types
from ckan.model import meta, Resource, domain_object
from sqlalchemy.ext.declarative import declarative_base


__all__ = [u"DataResourceColumnIndex", u"crc1153_data_resource_column_index_table"]

Base = declarative_base(
    metadata=meta.metadata,
    cls=domain_object.DomainObject,
)


class DataResourceColumnIndex(Base):
    __tablename__ = u"crc1153_data_resource_column_index"

    id = Column(u"id", _types.Integer, primary_key=True, nullable=False)
    resource_id = Column(
        u"resource_id",
        _types.UnicodeText,
        ForeignKey(u"resource.id"),
        nullable=False,
    )
    columns_names = Column(u"columns_names", _types.UnicodeText, nullable=False)
    resource = orm.relationship(
        Resource,
        backref=orm.backref(
            u"crc1153_data_resource_column_index",
            cascade=u"all, delete, delete-orphan",
        ),
    )

    def __init__(self, resource_id=None, columns_names=None):
        self.resource_id = resource_id
        self.columns_names = columns_names      



    @classmethod
    def get_all(cls, autoflush=True):
        query = meta.Session.query(cls)  
        query = query.autoflush(autoflush)
        return query.all()
     

    @classmethod
    def get_by_resource(cls, id, autoflush=True):
        if not id:
            return None

        exists = meta.Session.query(cls).filter(cls.resource_id==id).first() is not None
        if not exists:
            return False
        query = meta.Session.query(cls).filter(cls.resource_id==id)
        query = query.autoflush(autoflush)
        record = query.all()
        return record

    
    def get_resource(self):
        return self.resource


data_resource_column_index_table = DataResourceColumnIndex.__table__
