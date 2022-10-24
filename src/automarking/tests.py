# -*- coding: utf-8 -*-
"""
#####################################################
:mod:`automarking.tests` -- Automated Testing Support
#####################################################

.. moduleauthor:: Mark Hall <mark.hall@work.room3b.eu>, Dan Campbell <danielcampbell2097@hotmail.com>
"""
import json
from io import StringIO, BytesIO
from subprocess import Popen, PIPE, TimeoutExpired

HTML_VALIDATOR_URL = ["https://teaching.computing.edgehill.ac.uk/validator/html/"]


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

def run_html_validator(command, parameters, submission_file, timeout=60):
    
    feedback = ""
    with Popen([command] + parameters + HTML_VALIDATOR_URL, stdout=PIPE, stderr=PIPE) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            stdout = ""#stdout.decode('utf-8').replace("#StandWithUkraine", "")
            stderr = stderr.decode('utf-8').replace('#StandWithUkraine', "")
            
            if stdout != "":
                stdout_dic = json.loads(stdout)
                feedback = feedback + process_message(stdout_dic)

        except TimeoutExpired:
            process.kill()
            stdout = 'Validation failed due to timeout'
            stderr = 'Validation failed due to timeout'
        # if process.returncode == 0:
        #     submission_file.score = 2
        #     if stdout:
        #         submission_file.feedback.append(feedback)
        # else:
        #     submission_file.score = 1
        #     if stdout:
        #         submission_file.feedback.append(feedback)
        # 
        # Probably Ignore curl spits out too much crap
        #       if stderr:
        #         submission_file.feedback.append(stderr)
    