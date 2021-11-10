# Open python interpreter
# Copy paste following in interpreter

from jukebox.models import db

db.drop_all()
db.create_all()

from jukebox.models import User, Session, Song

u1 = User(username="kianworld123", password_hash="105023")
u2 = User(username="kyle123", password_hash="105023")
u3 = User(username="rece123", password_hash="105023")

db.session.add(u1)
db.session.add(u2)
db.session.add(u3)
db.session.commit()

User.query.all()

s1 = Session(name="12345")
s2 = Session(name="41234")

db.session.add(s1)
db.session.add(s2)
db.session.commit()

u1.session_id=Session.query.filter_by(name="12345").first().name
db.session.add(u1)
db.session.commit()
