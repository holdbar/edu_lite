import re
import os
from datetime import datetime, timedelta, date
from passlib.hash import sha256_crypt

from flask import render_template, flash, request, redirect, session, jsonify
from edu_lite import app, db
from .forms import LoginForm, RegistrationForm, TestForm, AttemptForm, FileForm, NewTestForm, PastAttemptsForm
from .models import Tests, Students, Questions, Answers, Attempts, Results
from flask_login import login_user, logout_user, login_required
from werkzeug import secure_filename
from .manage import add_questions



@app.route('/test', methods=['GET', 'POST'])
@login_required
def test():
    """Test view."""   

    form = TestForm()
    tests = [(t.id,t.name) for t in Tests.query.all()]
    form.test.choices = tests
    if request.method == "POST":
        session['test_id'] = form.test.data
        session['starttime'] = datetime.now()
        attempt = Attempts(student_id=session['user_id'],
                           starttime=session['starttime'],
                           test_id=session['test_id'])
        db.session.add(attempt)
        db.session.commit()
        return redirect('/test/attempt')
    return render_template('test.html',
                           title='Тесты',
                           form=form)




@app.route('/test/attempt', methods=['GET', 'POST'])
@login_required
def attempt():
    """Attempt view."""

    form = AttemptForm()
    questions = [(q.id,q.value,q.ismultiple) for q in Questions.query.filter_by(test_id=session['test_id']).all()]
    if request.method == "POST":
        attempt = Attempts.query.order_by(Attempts.starttime.desc()).filter_by(student_id=session['user_id'],
                                           test_id=session['test_id']).first()
        session['attempt_id'] = attempt.id
        for question in questions:
            if question[2] == 0:   # Check on single answer
                form_answer = request.form.get(str(question[0]))
                results = Results(attempt_id=attempt.id,
                                  question_id=question[0],
                                  fact_id=int(form_answer))
                db.session.add(results)
            else:
                form_answers = request.form.getlist(str(question[0]))
                int_form_answers =  [int(x) for x in form_answers]
                for answer in int_form_answers:
                    results = Results(attempt_id=attempt.id,
                                      question_id=question[0],
                                      fact_id=answer)
                    db.session.add(results)
        endtime = datetime.now()
        attempt.endtime = endtime
        db.session.commit()
        return redirect('/test/results')
    return render_template('attempt.html',
                            title='Тестирование',
                            form=form,
                            questions=questions)



@app.route('/test/results')
@login_required
def results():
    """Results view."""

    results_list = []    
    questions = [(q.id,q.value,q.ismultiple) for q in Questions.query.filter_by(test_id=session['test_id']).all()]  
    # Count of total result in format 'count of correct answers/count of all answers'
    total = 0
    for question in questions:
        fact_ids = [r.fact_id for r in Results.query.filter_by(attempt_id=session['attempt_id'], 
                                                               question_id=question[0]).all()]
        if question[2] == 0:
            correct_answer = Answers.query.filter_by(question_id=question[0], iscorrect=1).first()
            if correct_answer.id in fact_ids:
                total += 1
        if question[2] == 1:
            wrong = 0
            correct_answers = Answers.query.filter_by(question_id=question[0], iscorrect=1).all()
            for answer in correct_answers:
                if answer.id not in fact_ids:
                    wrong += 1
                for fact_id in fact_ids:
                    fact = Answers.query.get(fact_id)
                    if fact.iscorrect == 0:
                        wrong += 1
            if wrong == 0:
                total += 1
        answers = Answers.query.filter_by(question_id=question[0]).all()
        results_list.append([question[1], answers, fact_ids])
    count = 0
    for question in questions:
        count += 1
    total_result = str(total) + '/' + str(count)
    return render_template('results.html',
                            title='Результаты',
                            total_result=total_result,
                            results=results_list)


@app.route('/past_attempts')
@login_required
def past_attempts():
    """Past attempts view."""

    form = PastAttemptsForm()
    tests = [(t.id,t.name) for t in Tests.query.all()]
    form.test.choices = tests
    students = [(s.id,s.name) for s in Students.query.all()]
    form.student.choices = students
    return render_template('past_attempts.html',
                            title='Прошлые попытки',
                            form=form)



@app.route('/get_past_attempts', methods=['POST'])
@login_required
def get_past_attempts():
    """Util view for AJAX load of past attempts."""

    test_id = request.form['test']
    student_id = request.form['student']
    test_date = request.form['date']
    attempts_dict = {}
    test_day = datetime.strptime(test_date, '%Y-%m-%d')
    next_day = test_day + timedelta(days=1)
    #attempts = [(a.id, a.starttime, a.endtime) for a in Attempts.filter(Attempts.test_id==test_id,
    #                                                                    Attempts.student_id==student_id,
    #                                                                    Attempts.starttime>=test_day,
    #                                                                    Attempts.endtime <= next_day).all()]
    attempts = [(a.id, a.starttime, a.endtime) for a in db.session.query(Attempts).filter(Attempts.test_id==test_id,
                                                                                   Attempts.student_id==student_id,
                                                                                   Attempts.starttime>=test_day,
                                                                                   Attempts.endtime <= next_day).all()]
    for attempt in attempts:
        attempts_dict[str(attempt[0])] = {'start': attempt[1], 'end': attempt[2]}
    return jsonify(attempts_dict)


@app.route('/logout')
@login_required
def logout():
    """Logout view."""

    logout_user()
    return redirect('/login')





@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login view."""

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        form_name = form.name.data
        form_password = form.password.data
        form_remember = form.remember_me.data
        user = form.validate_user(form_name, form_password)
        if user:
                login_user(user, remember = form_remember)
                student = Students.query.get(session['user_id'])
                if student.isadmin == 1:
                    return redirect('/admin')
                else:
                    return redirect('/test')
    return render_template('login.html',
                           title='Вход',
                           form=form)




@app.route('/registration', methods=['GET', 'POST'])
@login_required
def registration():
    """Registration view."""

    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        form_name = form.name.data
        form_password = form.password.data
        form_password_repeat = form.password_repeat.data
        if form_password == form_password_repeat:
            form.register_user(form_name, form_password)
            return 'User {} was added'.format(form_name)
    return render_template('registration.html',
                           title='Registration',
                           form=form)




@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    """Admin view."""

    student = Students.query.get(session['user_id'])
    if student.isadmin != 1:
        return "Access denied!!!"
    else:
        form_file = FileForm()
        names = [(t.id,t.name) for t in Tests.query.all()]
        form_file.test.choices = names
        form_new_test = NewTestForm()
        form_reg = RegistrationForm()
        if request.method == 'POST' and form_file.file.data:
            filename = secure_filename(form_file.file.data.filename)
            form_file.file.data.save('uploads/' + filename)
            test_id = form_file.test.data
            add_questions(test_id,filename)
            message = 'Вопросы из файла {} добавлены'.format(filename) 
            return render_template('admin.html',
                                   title='Админка',
                                   message=message,
                                   form_new_test=form_new_test,
                                   form_reg=form_reg,
                                   form_file=form_file)
        if request.method == 'POST' and form_new_test.validate_on_submit():
            test_name = request.form.get('test_name') 
            new_test = Tests(name=test_name)
            db.session.add(new_test)
            db.session.commit()
            message = 'Добавлен тест {}'.format(form_new_test.test_name.data)
            return render_template('admin.html',
                                   title='Админка',
                                   message=message,
                                   form_new_test=form_new_test,
                                   form_reg=form_reg,
                                   form_file=form_file)
        if request.method == 'POST' and form_reg.validate_on_submit():
            form_name = form_reg.name.data
            form_password = form_reg.password.data
            form_password_repeat = form_reg.password_repeat.data
            if form_password == form_password_repeat:
                form_reg.register_user(str(form_name), form_password)
                message = 'Пользователь {} добавлен'.format(form_name)
                return render_template('admin.html',
                                       title='Админка',
                                       message=message,
                                       form_new_test=form_new_test,
                                       form_reg=form_reg,
                                       form_file=form_file)
        return render_template('admin.html',
                               title='Админка',
                               form_new_test=form_new_test,
                               form_reg=form_reg,
                               form_file=form_file)
        