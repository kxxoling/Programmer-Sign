import datetime

from flask import jsonify
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BasicMixin(object):

    id_ = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)          # First time the column is created.

    def to_json(self, *columns):
        dct = self.to_dict(*columns)
        for key in dct:
            if isinstance(dct[key], datetime.datetime):
                dct[key] = dct[key].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify(dct)

    def to_dict(self, *columns):
        dct = {}
        for col in columns:
            dct[col] = getattr(self, col)
        return dct

    def __unicode__(self):
        return "<Model %s>%d: %s" % (self.__class__.__name__, self.id_,
                                     getattr(self, 'name', None) or getattr(self, 'title', 'Untitled'))


class SessionMixin(object):
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self


class User(db.Model, BasicMixin, SessionMixin):
    __tablename__ = 'users'

    name = db.Column(db.String(100))
    email = db.Column(db.String(50))
    family_name = db.Column(db.String(100))
    role = db.Column(db.Integer)
    sighs = db.relationship('Sigh')
    tags = db.relationship('Tag')
    comments = db.relationship('Comment')


tag_identifier = db.Table('tag_identifier',
                          db.Column('tag_id', db.Integer, db.ForeignKey('tags.id_')),
                          db.Column('sigh_id', db.Integer, db.ForeignKey('sighs.id_')))


class Sigh(db.Model, BasicMixin, SessionMixin):
    __tablename__ = 'sighs'

    creator_id = db.Column(db.Integer, db.ForeignKey('users.id_'))
    content = db.Column(db.Text, nullable=False)
    type_ = db.Column(db.Enum('sigh', 'wtf', 'fml'), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment')
    tags = db.relationship('Tag', secondary=tag_identifier)


class Tag(db.Model, BasicMixin, SessionMixin):
    __tablename__ = 'tags'

    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(50), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id_'))


class Comment(db.Model, BasicMixin, SessionMixin):
    __tablename__ = 'comments'

    content = db.Column(db.Text, nullable=False)
    sigh_id = db.Column(db.Integer, db.ForeignKey('sighs.id_'))
    sigh = db.relationship('Sigh')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id_'))
    creator = db.relationship('User')
