'''
Send an HTTP POST request to the online SBOL validation tool
'''
import requests
from requests.exceptions import HTTPError
import json
import sys
import logging

def validate_sbol(sbol, validator_url = 'https://validator.sbolstandard.org/validate/'):

    # Structure POST request
    headers = {
        'Content-Type' : 'application/json',
        'Accept' : 'application/json',
        'charset' : 'utf-8'
    }
    data = {
                'options': {
                     'language' : 'SBOL2',
                     'test_equality': False,
                     'check_uri_compliance': False,
                     'check_completeness': False,
                     'check_best_practices': False,
                     'fail_on_first_error': False,
                     'provide_detailed_stack_trace': False,
                     'subset_uri': '',
                     'uri_prefix': '',
                     'version': '',
                     'insert_type': False,
                     'main_file_name': 'main file',
                     'diff_file_name': 'comparison file',
                 },
                 'return_file': False,
                 'main_file': sbol
          }
    try:
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        r = requests.post(validator_url, data=json.dumps(data), headers=headers)
        
        # If the response was successful, no Exception will be raised
        r.raise_for_status()
        return json.loads(r.text)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
       
if __name__ == '__main__':
    file = open(sys.argv[1], 'r')
    sbol = file.read()
    response = validate_sbol(sbol)
    print(response)
