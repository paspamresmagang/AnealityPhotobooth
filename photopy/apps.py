import sys
import os

from django.apps import AppConfig

# Tambahin path ke folder 'codeformer'
codeformer_path = os.path.join(os.path.dirname(__file__), 'codeformer')
if codeformer_path not in sys.path:
    sys.path.insert(0, codeformer_path)

# Baru import setelah path ditambahin
from processor import CodeFormerProcessor  # JANGAN pakai codeformer.processor ya!

class PhotopyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photopy'

    def ready(self):
        processor = CodeFormerProcessor()
        processor.initialize_model()