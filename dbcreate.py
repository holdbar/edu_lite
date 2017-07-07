from edu_lite import db
from edu_lite import models

db.create_all()
db.session.commit()