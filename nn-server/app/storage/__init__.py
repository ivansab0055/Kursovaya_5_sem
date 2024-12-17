import os

from path_definitions import current_path

local_main_s3_path = os.path.join(os.path.dirname(current_path), 'DATA', 'output')
local_test_s3_path = os.path.join(os.path.dirname(current_path), 'DATA', 'test')

remote_main_s3_path = 'data'
remote_test_s3_path = 'data-test'

if __name__ == '__main__':
    print(local_main_s3_path)
    print(local_test_s3_path)
