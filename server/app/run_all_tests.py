import argparse
import subprocess

test_files = [
    'tests/test_admin.py',
    'tests/test_captcha.py',
    'tests/test_change_password.py',
    'tests/test_check_token.py',
    'tests/test_confirm.py',
    'tests/test_email.py'
    'tests/test_forgot_password.py',
    'tests/test_login.py',
    'tests/test_mail_subscribe.py',
    'tests/test_refresh_token.py',
    'tests/test_forgot_password.py',
    'tests/test_signup.py',
    'tests/test_user.py',

]

# python run_all_tests.py --exclude tests/test_email.py
parser = argparse.ArgumentParser(description='Run unittests with option to exclude specific test file.')
parser.add_argument('--exclude', metavar='FILE', type=str, help='Test file to exclude from running')

args = parser.parse_args()

if args.exclude:
    try:
        test_files.remove(args.exclude)
        print(f'{args.exclude}')
    except ValueError:
        print(f"Warning: {args.exclude} not found in test_files.")

for test_file in test_files:
    result = subprocess.run(['python', '-m', 'unittest', test_file])
    if result.returncode != 0:
        print(f"Tests in {test_file} failed.")
        exit(result.returncode)
