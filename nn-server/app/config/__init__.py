import os

if os.environ.get('DEBUG') and os.environ.get('DEBUG') == 'false':
    from config.config_prod import DEBUG
elif os.environ.get('UNIT_TEST') in ['0', None]:
    from config.config_dev import DEBUG
else:
    from config.config_test import DEBUG
