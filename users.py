from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User

engine = create_engine('sqlite:///PQs.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Dominique Theodore", email="dominique.theodore86@gmail.com", role="admin")
User2 = User(name="Ronnie Antoine", email="jimmy.joplin@gmail.com", role="admin")
session.add(User1)
session.add(User2)
session.commit()