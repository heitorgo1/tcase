"""
tcase

Description:
    Create folders with input and output for problems.

Usage:
  tcase [--contest]
        [--online-judge=JUDGE]
        <problem_or_contest_ids>...

Options:
  -c, --contest                     Contest mode.
  -o, --online-judge=JUDGE          Online judge name. [default: codeforces]
"""
import os, errno
from docopt import docopt
import config
import requests
from bs4 import BeautifulSoup
import subprocess

def create_folder(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def readPdfFile(filepath):
    proc = subprocess.Popen(['pdftotext', '-raw' , filepath, '-'], stdout=subprocess.PIPE)
    text = proc.stdout.read().decode('utf-8')
    return text



class Problem:

    def __init__(self, id, name, timelimit, testcases=[]):
        self.id = id
        self.name = name
        self.timelimit = timelimit
        self.testcases = testcases

    def addTestCase (self, testcase):
        self.testcases.append(testcase)

    def printProblem(self):
        input_folder = '{}/{}/input'.format(os.getcwd(), self.id)
        output_folder = '{}/{}/output'.format(os.getcwd(), self.id)
        create_folder(input_folder)
        create_folder(output_folder)

        with open(os.path.join(os.getcwd(), self.id,  'info.txt'), 'w') as f:
            f.write('ID={}\n'.format(self.id))
            f.write('NAME={}\n'.format(self.name))
            f.write('TIMELIMIT={}\n'.format(self.timelimit))

        for index, case in enumerate(self.testcases):
            with open(os.path.join(input_folder, str(index)+'.in'), 'w') as f:
                f.write(case[0]);

            with open(os.path.join(output_folder, str(index)+'.out'), 'w') as f:
                f.write(case[1]);

        def __str__(self):
            return (self.id, self.name, self.timelimit, self.testcases).__str__()


class CfContestParser:
    pass


class UvaProblemParser:

    host = config.CONFIG['uva']['host']

    def __init__(self, problem_id):
        prefix = problem_id[:-2]
        path = config.CONFIG['uva']['formats']['problem'].format(self.host,prefix,problem_id)
        req = requests.get(path)

        if req.status_code != 200:
            raise Exception('Invalid page: {}'.format(path))
        
        with open('/tmp/{}.pdf'.format(problem_id), 'wb') as fd:
            fd.write(req.content)
        
        self.problem_id = problem_id

    
    def to_problem(self):
        stats = requests.get(config.CONFIG['uva']['formats']['stats'].format(self.problem_id)).json()
        raw_text = readPdfFile('/tmp/{}.pdf'.format(self.problem_id))
        id = self.problem_id
        name = stats['title']
        timelimit = int(stats['rtl']/1000)

        input_idx = raw_text.index('Sample Input')
        raw_text = raw_text[input_idx:]
        isInput = False
        isOutput = False
        input_lines = []
        output_lines = []
        for line in raw_text.splitlines():
            if line == 'Sample Input':
                isInput = True
                isOutput = False
                continue
            if line == 'Sample Output':
                isOutput = True
                isInput = False
                continue
            if '{} – {}'.format(id, name) in line:
                continue
            if not line:
                continue
            
            if isInput:
                input_lines.append(line)
            elif isOutput:
                output_lines.append(line)
        
        testcases = [('\n'.join(input_lines)+'\n', '\n'.join(output_lines)+'\n')]

        return Problem(id,name,timelimit,testcases)




class CfProblemParser:

    host = config.CONFIG['cf']['host']

    def __init__(self, problem_id):
        problem_id = problem_id.upper()
        path = config.CONFIG['cf']['formats']['problem'].format(self.host,problem_id[:-1],problem_id[-1])
        req = requests.get(path)

        if req.status_code != 200:
            raise Exception('Invalid page: {}'.format(path))

        html_doc = req.text
        self.problem_id = problem_id
        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def str_tag(self, tag):
        if isinstance(tag, str):
            return tag
        if tag.name == 'br':
            return '\n'
        return tag.name

    def get_samples(self, kind):
        sample_input = self.soup.find_all(class_=kind)
        sample_input = [x.contents[1].contents for x in sample_input]
        sample_input = [[self.str_tag(y) for y in x] for x in sample_input]
        sample_input = [''.join(x) for x in sample_input]
        return sample_input

    def to_problem(self):
        id = self.problem_id
        timelimit = self.soup.find_all(class_='time-limit')[0].contents[1].split(' ')[0]
        name = self.soup.find_all(class_='title')[0].contents[0]
        sample_input = self.get_samples('input')
        sample_output = self.get_samples('output')

        testcases = list(zip(sample_input, sample_output))

        return Problem(id,name,timelimit,testcases)


class UriProblemParser:

    host = config.CONFIG['uri']['host']

    def __init__(self, problem_id):
        path = config.CONFIG['uri']['formats']['problem'].format(self.host, problem_id)
        req = requests.get(path)

        if req.status_code != 200:
            raise Exception('Invalid page: {}'.format(path))

        html_doc = req.text
        self.problem_id = problem_id
        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def str_tag(self, tag):
        if isinstance(tag, str):
            return tag.strip()
        if tag.name == 'br':
            return '\n'
        return tag.name

    def to_problem(self):
        id = self.problem_id
        name = self.soup.find(class_='header').h1.string
        timelimit = self.soup.find(class_='header').strong.string.split(' ')[1]
        testcases = self.soup.find_all(class_='division')
        ins = [x.p.contents for x in testcases]
        ins = [''.join([self.str_tag(y) for y in x]) for x in ins]
        outs = [x.next_sibling.next_sibling.p.contents for x in testcases]
        outs = [''.join([self.str_tag(y) for y in x]) for x in outs]
        testcases = list(zip(ins,outs));

        return Problem(id,name,timelimit,testcases)

if __name__ == '__main__':
    options = docopt(__doc__, version='1.0.0', options_first=True)

    if options['--online-judge'] in ['cf', 'codeforces']:
        for problem_id in options['<problem_or_contest_ids>']:
            problem = CfProblemParser(problem_id).to_problem()
            problem.printProblem()
    elif options['--online-judge'] in ['uva']:
        for problem_id in options['<problem_or_contest_ids>']:
            problem = UvaProblemParser(problem_id).to_problem()
            problem.printProblem()
    elif options['--online-judge'] in ['uri']:
        for problem_id in options['<problem_or_contest_ids>']:
            problem = UriProblemParser(problem_id).to_problem()
            problem.printProblem()
    else:
        print('{} Not implemented.'.format(options['--online-judge']))