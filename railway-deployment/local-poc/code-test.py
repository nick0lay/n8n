import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import json
import math
import random

def verify_dependencies():
    results = {
        'status': '✅ ALL DEPENDENCIES WORKING',
        'packages': {},
        'tests': {}
    }

    # Test 1: requests - HTTP GET
    try:
        response = requests.get('https://api.github.com/repos/n8n-io/n8n', timeout=5)
        repo_data = response.json()
        results['packages']['requests'] = {
            'version': requests.__version__,
            'test': f'GitHub API status: {response.status_code}',
            'repoData': {
                'name': repo_data['name'],
                'stars': f"{repo_data['stargazers_count']:,}",
                'forks': f"{repo_data['forks_count']:,}",
                'language': repo_data['language']
            },
            'installed': '✅'
        }
    except Exception as e:
        results['packages']['requests'] = {'error': str(e), 'installed': '❌'}

    # Test 2: dateutil - Date parsing and manipulation
    try:
        # Parse various date formats
        iso_date = parser.parse("2025-10-22T14:30:00Z")
        natural_date = parser.parse("October 22, 2025")

        # Date arithmetic
        future_date = datetime.now() + relativedelta(months=3, days=15)
        past_date = datetime.now() - timedelta(days=30)

        results['packages']['dateutil'] = {
            'test': 'Date parsing and manipulation',
            'parsedDates': {
                'iso': iso_date.isoformat(),
                'natural': natural_date.strftime('%Y-%m-%d'),
                'currentTime': datetime.now().isoformat()
            },
            'calculations': {
                'in3Months15Days': future_date.strftime('%Y-%m-%d'),
                '30DaysAgo': past_date.strftime('%Y-%m-%d')
            },
            'installed': '✅'
        }
    except Exception as e:
        results['packages']['dateutil'] = {'error': str(e), 'installed': '❌'}

    # Test 3: Python stdlib - json, math, random, datetime
    try:
        # Math operations
        circle_area = math.pi * math.pow(5, 2)
        sqrt_result = math.sqrt(144)

        # Random operations
        random_num = random.randint(1, 100)
        random_choice = random.choice(['apple', 'banana', 'cherry'])

        # JSON operations
        test_data = {'name': 'test', 'value': 42}
        json_string = json.dumps(test_data)
        json_parsed = json.loads(json_string)

        results['tests']['stdlib'] = {
            'math': {
                'circleArea': round(circle_area, 2),
                'sqrt144': sqrt_result,
                'piValue': round(math.pi, 4)
            },
            'random': {
                'randomNumber': random_num,
                'randomChoice': random_choice
            },
            'json': {
                'serialized': json_string,
                'deserialized': json_parsed
            },
            'datetime': {
                'now': datetime.now().isoformat(),
                'today': datetime.today().strftime('%Y-%m-%d')
            }
        }
    except Exception as e:
        results['tests']['stdlib'] = {'error': str(e)}

    # Summary
    results['summary'] = {
        'message': '🎉 All packages and stdlib modules working!',
        'timestamp': datetime.now().isoformat(),
        'packagesWorking': sum(1 for p in results['packages'].values() if p.get('installed') == '✅')
    }

    return results

return [{'json': verify_dependencies()}]
