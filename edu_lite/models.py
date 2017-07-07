from edu_lite import db


class Tests(db.Model):
    """Tests model."""

    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Questions(db.Model):
    """Questions model."""

    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String)
    test_id = db.Column(db.Integer, db.ForeignKey("tests.id"))
    ismultiple = db.Column(db.Integer)



class Answers(db.Model):
    """Answers model."""

    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    iscorrect = db.Column(db.Integer)



class Attempts(db.Model):
    """Attempts model."""

    __tablename__ = 'attempts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    starttime = db.Column(db.DateTime)
    endtime = db.Column(db.DateTime)
    test_id = db.Column(db.Integer, db.ForeignKey("tests.id"))



class Results(db.Model):
    """Results model."""

    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    fact_id = db.Column(db.Integer)



class Students(db.Model):
    """Users(students) model."""

    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    isadmin = db.Column(db.Integer)


    def __init__(self, name, password, isadmin):
        self.name = name
        self.password = password
        self.isadmin = isadmin
        

    # These methods go with flask_login  
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)




