It's simple system without any groups. You just need to create a test, upload questions and create students accounts.

Getting started

1. Download code.
2. Create virtualenv with Python 3.x.
3. Run 'pip install -r requirements.txt' command.
4. Run 'createdb.py' and 'createadmin.py' scripts.
5. Launch app with 'run.py' script.

Uploading tests

1. Open app page in browser(by default it's localhost:5000)
2. Get autorized as admin user.
3. Create test on admin page.
4. Choose test and file with questions in the questions form on admin page.

Questions preparation

Example of format can be found in 'questions_sample.txt'
Questions with one correct answer are marked with '?' at the beginning of the line.
Questions with multiple correct answers are marked with '#' at the beginning of the line.
Correct questions are marked with '=' at the beginning of the line.
Every block of answers must be caught in '{' and '}' lines.

Creating students

1. Open app page in browser(by default it's localhost:5000)
2. Get autorized as admin user.
3. Create students accounts on admin page.
