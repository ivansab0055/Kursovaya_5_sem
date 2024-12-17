import os

if os.environ.get('DEBUG') and os.environ.get('DEBUG') == 'false':
    from config.config_prod import DEBUG
    from config.config_prod import REACT_APP_RECAPTCHA_SECRET_KEY
elif os.environ.get('UNIT_TEST') in ['0', None]:
    from config.config_dev import DEBUG
    from config.config_dev import REACT_APP_RECAPTCHA_SECRET_KEY
else:
    from config.config_test import DEBUG
    from config.config_test import REACT_APP_RECAPTCHA_SECRET_KEY
