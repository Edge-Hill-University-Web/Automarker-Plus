# -*- coding: utf-8 -*-
"""
#####################################################
:mod:`automarking.tests` -- Automated Testing Support
#####################################################

.. moduleauthor:: Mark Hall <mark.hall@work.room3b.eu>, Dan Campbell <danielcampbell2097@hotmail.com>
"""
import json
import re
import urllib.parse
from io import StringIO, BytesIO
from subprocess import Popen, PIPE, TimeoutExpired

HTML_VALIDATOR_URL = "https://teaching.computing.edgehill.ac.uk/validator/html?"
CSS_VALIDATOR_URL = "https://teaching.computing.edgehill.ac.uk/validator/css/validator?"

def format_feedback(feedback, start_tag='\t<li>', end_tag='</li>',):
    return f"{start_tag}{feedback}{end_tag}"

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
    
    if isinstance(source, str):
        source = source.splitlines(True)
        
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


def run_test(command, parameters, submission_file, timeout=60, correct_points=4, attempt_points=2, simple=False):

    with Popen([command] + parameters, stdout=PIPE, stderr=PIPE) as process:
        try:

            stdout, stderr = process.communicate(timeout=timeout)
            stdout = stdout.decode('utf-8').replace("#StandWithUkraine", "")
            stderr = stderr.decode('utf-8').replace('#StandWithUkraine', "")  

            if 'at reverse (merge' in stdout:
                stdout= 'RangeError: Maximum call stack size exceeded. Your code just keeps adding function calls to the stack\n'
            
            if simple:
                
                # Order of this list is important for the feedback!
                console_streams = [stderr, stdout]
                for stream in console_streams:
                    if not not stream: 
                        if submission_file.spec.identifier.endswith('.php'): # Handle PHPUnit Output
                        
                            if'OK' in stream: # PASS
                                stdout = "PHP Unit: Test Passed"
                                submission_file.score = correct_points
                                submission_file.feedback.append(format_feedback(stdout)) 
                                submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt and 2 marks for passing the unit test/s"))
                            elif 'PHP Warning' in stream:
                                stream = stream.split(sep=',')[0]
                                submission_file.feedback.append(format_feedback(stream)) 
                            elif 'ParseError: syntax error' in stream:
                                submission_file.score = attempt_points
                                submission_file.feedback.append(format_feedback("PHP Fatal error:  Uncaught ParseError: syntax error")) 
                                submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt"))
                            elif 'Call to undefined function' in stream:
                                stream = re.search(r'Error: (.+?)\n', stream).group().strip()
                                submission_file.score = attempt_points
                                submission_file.feedback.append(format_feedback(f'{stream}')) 
                                submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt")) 
                                
                            elif 'because the name is already in use' in stream:
                                stream = re.search(r'PHP Fatal error: (.+?) in (.+?) ', stream)
                                submission_file.score = attempt_points
                                submission_file.feedback.append(format_feedback(f'PHP Fatal error: {stream.group(1)}')) 
                                submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt")) 
                            elif 'OK' not in stream:# Fail
                                try:
                                    stream  = re.search(r'(There was \d (error|failure):)[\s\S]([\w\s]*.*){1,2}', stdout, re.MULTILINE).group().strip()
                                    stream = re.sub(r'\d\)\s{1,}question_\d{1,}::test', '', stream)
                                    submission_file.score = attempt_points
                                    submission_file.feedback.append(format_feedback(stream.replace('\n', ' ')))  
                                    submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt")) 
                                except Exception as e:
                                    print(f'{e}\n There was an error processing...\n {stream} \n')    
                      
                        if submission_file.spec.identifier.endswith('.js'): # Java Script   
                                        
                            if 'failing' in stream:
                                stream = re.search(r'(^.*\wError:*.*)', stream, re.MULTILINE).group().strip()
                                submission_file.score = attempt_points
                                submission_file.feedback.append(format_feedback(stream))
                                submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt"))
                            elif '✔' in stream:
                                stream = "Mocha: Test Passed"
                                submission_file.score = correct_points
                                submission_file.feedback.append(format_feedback(stream))
                                submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt and 2 marks for passing the unit test/s"))
                            
                            elif 'Error' in stream:
                                stream = re.search(r'.*Error+.*', stream.strip()).group().strip()
                                submission_file.feedback.append(format_feedback(stream))
                                submission_file.feedback.append(format_feedback("You have been awarded 2 marks for an attempt"))
                                
            
            elif not simple:
                
                if process.returncode == 0:
                    submission_file.score = correct_points
                    if stdout:
                        submission_file.feedback.append(format_feedback(stdout))
                else:
                    submission_file.score = attempt_points
                    if stdout:
                        submission_file.feedback.append(format_feedback(stdout))
                    if stderr:
                        submission_file.feedback.append(format_feedback(stderr))                
        
        
        except TimeoutExpired:
            process.kill()
            stdout = None
            stderr = 'Test failed due to timeout'
            
               
def run_jest_test(command = "", parameters=[], timeout=30):

    with Popen([command] + parameters, stdout=PIPE, stderr=PIPE) as process:
        try:
            
            stdout, stderr = process.communicate(timeout=timeout)
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')
            process.kill()


        except TimeoutExpired:
            process.kill()
            stdout = None
            stderr = 'Test failed due to timeout'
            
        return {'out': stdout, 'err': stderr, 'code': process.returncode}



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

    command = [cmd, '-X', 'POST', HTML_VALIDATOR_URL + "out={}".format(output_format), '--data-binary',
               "{}".format(data), '-H', "Content-Type: text/html;charset=utf-8"]

    with Popen(command, stdout=PIPE,
               stderr=PIPE) as process:

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')

            if stdout != "":
                if output_format == 'json':
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


def run_css_validator(path_to_submission_file, output_format='json', timeout=60, command='curl'):
    feedback = ""

    safeCSS = urllib.parse.quote(open(path_to_submission_file).read(), safe='/')

    with Popen([command] + [CSS_VALIDATOR_URL + "output={}&text={}&lang=en".format(output_format, safeCSS)],
               stdout=PIPE,
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
