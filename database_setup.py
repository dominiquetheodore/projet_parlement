import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

engine = create_engine('sqlite:///PQs.db')
DBSession = sessionmaker(bind=engine)
Sess = DBSession()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=True)
    role = Column(String(250), default="subscriber")

    @property 
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email':self.email,
            'picture':self.picture,
            'role':self.role
        }

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    count = Column(Integer)

    @classmethod
    def count_pqs(self, cls):
        print cls.id
        cnt = Sess.query(PQ.id).filter(PQ.session_id==cls.id).count()
        print cnt
        return cnt

    @property 
    def serialize(self):
        return {
            'id': self.id,
            'date': self.date,
        }

class Party(Base):
    __tablename__ = 'parties'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    color = Column(String(100))

    @property 
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'color':self.color,
        }

class Deputy(Base):
    __tablename__ = 'deputies'

    id = Column(Integer, primary_key=True)
    name = Column(String(2000))
    first_name = Column(String(2000))
    title = Column(String(500))
    img_url = Column(String(500), default="face.png")
    party = relationship(Party)
    party_id = Column(Integer, ForeignKey('parties.id'))
    constituency = Column(Integer)
    count = Column(Integer)
    bio = Column(String(400))

    @classmethod
    def count_pqs(self, cls):
        cnt = Sess.query(PQ.id).filter(PQ.deputy_id==cls.id).count()
        return cnt

    @property 
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'img_url':self.img_url, 
            'first_name': self.first_name,
            'constituency': self.constituency,
            'bio': self.bio
        }

class PQ(Base):
    __tablename__ = 'pqs'

    id = Column(Integer, primary_key=True)
    pq_ref = Column(String(2000))
    file_name = Column(String(2000))
    pq = Column(String(2000))
    answer = Column(String(60000), default="answer goes here")
    title = Column(String(2000))
    deputy = relationship(Deputy)
    deputy_id = Column(Integer, ForeignKey('deputies.id'))
    session = relationship(Session)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    date_asked = Column(String(2000))
    asked_by = Column(String(200))
    asked_to = Column(String(2000))

    @property 
    def serialize(self):
        return {
            'id': self.id,
            'pq_ref': self.pq_ref,
            'file_name':self.file_name,
            'title': self.title,
            'pq': self.pq,
            'answer':self.answer,
            'date_asked': self.date_asked,
            'asked_by': self.asked_by,
            'asked_to':self.asked_to
        }

class PNQ(Base):
    __tablename__ = 'pnqs'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(2000))
    pnq = Column(String(2000))
    answer = Column(String(60000), default="answer goes here")
    title = Column(String(2000))
    session = relationship(Session)
    session_id = Column(Integer, ForeignKey('sessions.id'))

    @property 
    def serialize(self):
        return {
            'id': self.id,
            'file_name':self.file_name,
            'title': self.title,
            'pnq': self.pnq,
            'answer':self.answer,
        }

class Constituency(Base):
    __tablename__ = 'constituencies'

    id = Column(Integer, primary_key=True)
    constituency = Column(String(100))

    @property 
    def serialize(self):
        return {
            'id': self.id,
            'constituency': self.constituency,
        }


engine = create_engine('sqlite:///PQs.db')


Base.metadata.create_all(engine)