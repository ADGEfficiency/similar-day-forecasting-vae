import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()
HOME = os.getenv('PROJECT_HOME')
DATAHOME = Path(HOME, 'data')
MODELHOME = Path(HOME, 'models')

regions = ['TAS1', 'SA1', 'VIC1', 'NSW1', 'QLD1']
