# load.py
import os
from django.contrib.gis.utils import LayerMapping
from app.models import Master

mapping = {
    'title': 'title',
    'manufucturer':'manufacturer',
    'jan':'jan',
    'mpn':'mpn',
    'category':'category',
    'subcategory':'subcategory'
}

master_csv = os.path.abspath(os.path.join(os.path.dirname(__file__),'','master.csv'))
def run(verbose=True):
    lm = LayerMapping(Master,master_csv,mapping=mapping,transform=False,encoding='UTF-8')
    lm.save(strict=True,verbose=verbose)