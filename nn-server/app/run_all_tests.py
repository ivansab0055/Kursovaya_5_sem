import argparse
import platform
import subprocess

test_files = [
    'tests/test_create_folders.py',
    'tests/test_predict.py',
    'tests/test_result.py',
    'tests/test_S3.py',
    'tests/test_status.py',
    'tests/test_stop.py',
]

if platform.system() == 'Windows':
    test_files.remove('tests/test_stop.py')

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
