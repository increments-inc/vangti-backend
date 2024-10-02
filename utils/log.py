import logging
from django.conf import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
    filename=f'{settings.LOG_DIR}/vangti.log',
)

