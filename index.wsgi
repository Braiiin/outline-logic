#!/usr/bin/python3

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/logic.outline.braiiin.com/logic")
sys.path.insert(0,"/var/www/logic.outline.braiiin.com")

from outline_logic import create_outline_app

application = create_outline_app(root='outline_logic', config='ProductionConfig')

if __name__ == "__main__":
    application.run(**application.config['INIT'])
