# -*- coding: utf-8 -*-
"""
#####################################################
:mod:`automarking.tests` -- Automated Testing Support
#####################################################

.. moduleauthor:: Mark Hall <mark.hall@work.room3b.eu>, Dan Campbell <danielcampbell2097@hotmail.com>
"""
import json
import urllib.parse
from io import StringIO, BytesIO
from subprocess import Popen, PIPE, TimeoutExpired


HTML_VALIDATOR_URL = "https://teaching.computing.edgehill.ac.uk/validator/html?"
CSS_VALIDATOR_URL = "https://teaching.computing.edgehill.ac.uk/validator/css/validator?"


def extract_code(source, start_identifier='// StartStudentCode', end_identifier='// EndStudentCode'):
    pre = []
    code = []
    post = []
    state = 0
    if isinstance(source, BytesIO):
        try:
            source = StringIO(source.read().decode('utf-8'))
        except UnicodeDecodeError:
            try:
                source = StringIO(source.read().decode('latin-1'))
            except UnicodeDecodeError:
                try:
                    source = StringIO(source.read().decode('ascii'))
                except UnicodeDecodeError:
                    print('Could not decode file')
                    sourced = StringIO('')
    for line in source:
        if state == 0 and line.strip() == start_identifier:
            state = 1
        elif state == 1 and line.strip() == end_identifier:
            state = 2
        elif state == 0:
            pre.append(line)
        elif state == 1:
            code.append(line)
        elif state == 2:
            post.append(line)
    return ('\n'.join(pre), '\n'.join(code), '\n'.join(post))


def merge_code(base, overlay, start_identifier='// StartStudentCode', end_identifier='// EndStudentCode'):
    pre, _, post = extract_code(base, start_identifier, end_identifier)
    _, code, _ = extract_code(overlay, start_identifier, end_identifier)
    return '\n'.join([pre, code, post])


def run_test(command, parameters, submission_file, timeout=60):
    with Popen([command] + parameters, stdout=PIPE, stderr=PIPE) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            stdout = stdout.decode('utf-8').replace("#StandWithUkraine", "")
            stderr = stderr.decode('utf-8').replace('#StandWithUkraine', "")
        except TimeoutExpired:
            process.kill()
            stdout = None
            stderr = 'Test failed due to timeout'
        if process.returncode == 0:
            submission_file.score = 2
            if stdout:
                submission_file.feedback.append(stdout)
        else:
            submission_file.score = 1
            if stdout:
                submission_file.feedback.append(stdout)
            if stderr:
                submission_file.feedback.append(stderr)


def process_message(json):
    message = ""
    for msg in json['messages']:

        if message == "":
            message = "[Type: {}, SubType: {}, Message: {}".format(msg['type'], msg['subType'], msg['message'])
        else:
            message = message + "\n[Type: {}, SubType: {}, Message: {}".format(msg['type'], msg['subType'],
                                                                               msg['message'])
            if 'firstLine' in msg.keys():
                message = message + "At Line: {}".format(str(msg['firstLine']))
            if 'lastLine' in msg.keys():
                message = message + "Until Line: {}".format(str(msg['lastLine']))
            message = message + "]"
    return message

'''
output_format options:
none: HTML
xhtml: XHTML
xml: XML
json: JSON
gnu: GNU error format
text: Human-readable text (not for machine parsing)

'''
def run_html_validator(path_to_submission_file, output_format='json', timeout=60, cmd='curl'):
    feedback = ""

    data = open(path_to_submission_file, encoding="utf-8").read()


    command = [cmd, '-X', 'POST', HTML_VALIDATOR_URL+"out={}".format(output_format), '--data-binary', "{}".format(data), '-H', "Content-Type: text/html;charset=utf-8"]

    with Popen(command, stdout=PIPE,
               stderr=PIPE) as process:

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')

            if stdout != "":
                stdout_dic = json.loads(stdout)
                feedback = stdout_dic

        except TimeoutExpired:
            process.kill()
            feedback = 'Validation failed due to timeout'

    return feedback

'''
Triggers the various `outputs_formats` of the validator. The Possible formats are 
    - text/html 
    - html
    - xhtml 
    - application/soap+xml
    - text/plain
    - text
'''
def run_css_validator(path_to_submission_file ,output_format='text', timeout=60, command='curl'):
    feedback = ""

    safeCSS = urllib.parse.quote(open(path_to_submission_file).read())

    with Popen([command] + [CSS_VALIDATOR_URL+"output={}&text={}&lang=en".format(output_format, safeCSS)], stdout=PIPE,
               stderr=PIPE) as process:

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')

            if stdout != "":

                    feedback = stdout

        except TimeoutExpired:
            process.kill()
            feedback = 'Validation failed due to timeout'

    return feedback



print(run_html_validator("question_01.html", output_format='json', timeout=60, cmd='curl'))
