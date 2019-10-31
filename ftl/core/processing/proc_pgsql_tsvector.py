from django.contrib.postgres.search import SearchVector
from django.db.models import F

from core.processing.ftl_processing import FTLDocProcessingBase

DEFAULT_SEARCH_VECTOR = SearchVector('content_text', weight='C', config=F('language')) \
                        + SearchVector('note', weight='B', config=F('language')) \
                        + SearchVector('title', weight='A', config=F('language'))

FALLBACK_SEARCH_VECTOR = SearchVector('content_text', weight='C', config='simple') \
                + SearchVector('note', weight='B', config='simple') \
                + SearchVector('title', weight='A', config='simple')


class FTLSearchEnginePgSQLTSVector(FTLDocProcessingBase):
    def process(self, ftl_doc, force):
        if force or not ftl_doc.tsvector:
            if ftl_doc.language:
                ftl_doc.tsvector = DEFAULT_SEARCH_VECTOR
            else:
                ftl_doc.tsvector = FALLBACK_SEARCH_VECTOR
            ftl_doc.save()
