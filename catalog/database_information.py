
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *
engine = create_engine('sqlite:///Books.db')
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

session.query(Category).delete()


session.query(Book).delete()


session.query(User).delete()
# create user

User1 = User(name="Reem", email="alsolamy.reem@gmail.com",
             picture="""https://cdn2.iconfinder.com/data/icons/
             business-and-finance-related-hand-gestures/256/
             face_female_blank_user_avatar_mannequin-512.png""")
session.add(User1)
session.commit()

# Novels
category1 = Category(user_id=1, name="Novel")
session.add(category1)
session.commit()

# Health & Fitness
category2 = Category(user_id=1, name="Health & Fitness")
session.add(category2)
session.commit()

# Technology
category3 = Category(user_id=1, name="Technology")
session.add(category3)
session.commit()

# Marketing
category4 = Category(user_id=1, name="Marketing")
session.add(category4)
session.commit()

# History
category5 = Category(user_id=1, name="History")
session.add(category5)
session.commit()

# Poetry
category6 = Category(user_id=1, name="Poetry")
session.add(category6)
session.commit()

# Politics
category7 = Category(user_id=1, name="Politics")
session.add(category7)
session.commit()

book1 = Book(
    name="The Forty Rules of Love: A Novel of Rumi",
    file_link="""https://bit.ly/2GZREHr""",
    picture="""https://bit.ly/2Ru6pX9""",
    author="Elif Shafak",
    yearOfEmission="2013",
    numOfPage="229 pages",
    category=category1,
    user_id=1
    )
session.add(book1)
session.commit()

book2 = Book(
    name="The Complete Yoga Poses",
    file_link="""https://bit.ly/2LSm2Cl""",
    picture="""https://bit.ly/2QpkMY4""",
    author="Daniel Lacerda",
    yearOfEmission="2016",
    numOfPage="1132 pages",
    category=category2,
    user_id=1
    )
session.add(book2)
session.commit()

book3 = Book(
    name="Python Data Science Cookbook",
    file_link="""https://bit.ly/2yjl5g6""",
    picture="""https://bit.ly/2C6WTzi""",
    author="Gopi Subramanian",
    yearOfEmission="2015",
    numOfPage="755 pages",
    category=category3,
    user_id=1
    )
session.add(book3)
session.commit()

book4 = Book(
    name="Digital Marketing Analytics",
    file_link="""https://bit.ly/1tTqaEG""",
    picture="""https://bit.ly/2SDAbpx""",
    author="Chuck Hemann",
    yearOfEmission="2013",
    numOfPage="385 pages",
    category=category4,
    user_id=1
    )
session.add(book4)
session.commit()

book5 = Book(
    name="The Secret History Of The World",
    file_link="""https://bit.ly/2Fcs0wA""",
    picture="""https://bit.ly/2FcsmmU""",
    author="Laura Knight-Jadczyk",
    yearOfEmission="2006",
    numOfPage="812 Pages",
    category=category5,
    user_id=1
    )
session.add(book5)
session.commit()

book6 = Book(
    name="""The Cambridge Companion to Victorian
    Poetry (Cambridge Companions to Literature)""",
    file_link="""https://bit.ly/2FeoLVC""",
    picture="""https://bit.ly/2sctn6J""",
    author="Joseph Bristow",
    yearOfEmission="2010",
    numOfPage="360 pages",
    category=category6,
    user_id=1
    )
session.add(book6)
session.commit()

book7 = Book(
    name="The Nature of Political Theory",
    file_link="""https://bit.ly/2TuPUat""",
    picture="""https://bit.ly/2GW0ar6""",
    author="Andrew Vincent",
    yearOfEmission="2007",
    numOfPage="365 pages",
    category=category7,
    user_id=1
    )
session.add(book7)
session.commit()





