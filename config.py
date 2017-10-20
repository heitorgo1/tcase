from __future__ import print_function

CONFIG = {
    'cf': {
        'host': 'http://codeforces.com',
        'formats': {
            'contest': '{}/contest/{}',
            'contest_problem': '{}/contest/{}/problem/{}',
            'problem': '{}/problemset/problem/{}/{}'
        }
    },
    'uri': {
        'host': 'https://www.urionlinejudge.com.br',
        'formats': {
            'contest': '{}/judge/en/challenges/contest/{}',
            'contest_problem': '{}/judge/en/challenges/view/{}/{}',
            'problem': '{}/repository/UOJ_{}_en.html'
        }
    },
    'uva': {
        'host': 'https://uva.onlinejudge.org',
        'formats': {
            'problem': '{}/external/{}/{}.pdf',
            'stats': 'https://uhunt.onlinejudge.org/api/p/num/{}'
        }
    }
}

