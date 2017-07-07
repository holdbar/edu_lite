import re
import os
from edu_lite import db
from edu_lite import models


def add_questions(test_id, file_name):
    """
    Add questions.

    Parse file with questions and import
    questions to db.
    """

    read_file = open('uploads/' + file_name)
    question_string = read_file.read()

    item_pattern = r'[\?#][^{]*{?[^{]*}'

    search = re.findall(item_pattern,question_string)

    item_list = []

    for item in search:
        item_list.append(item.split('\n'))
    for item in item_list:
        item.remove('{')
        item.remove('}')

    for item in item_list:
        for i in item:
            if i[0] == '?':
                question = models.Questions(value=i[1:],test_id=test_id,ismultiple=0)
                db.session.add(question)
                db.session.commit()
            elif i[0] == '#':
                question = models.Questions(value=i[1:],test_id=test_id,ismultiple=1)
                db.session.add(question)
                db.session.commit()
            elif i[0] == '=':
                question = models.Questions.query.filter_by(value=item[0][1:]).first()
                answer = models.Answers(value=i[1:],question_id=question.id,iscorrect=1)
                db.session.add(answer)
                db.session.commit()
            else:
                question = models.Questions.query.filter_by(value=item[0][1:]).first()
                answer = models.Answers(value=i,question_id=question.id,iscorrect=0)
                db.session.add(answer)
                db.session.commit()

