import importlib
import inspect
import logging
from concurrent.futures.thread import ThreadPoolExecutor

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db.models import F

SEARCH_VECTOR = SearchVector('content_text', weight='C', config=F('language')) \
                + SearchVector('note', weight='B', config=F('language')) \
                + SearchVector('title', weight='A', config=F('language'))

logger = logging.getLogger(__name__)


class FTLDocumentProcessing:
    """
    A base document processing class, to be used for adding processing to document such as OCR,
    text extraction, etc.
    """
    executor = None
    plugins = list()

    def __init__(self, max_workers=1):
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ftl_doc_processing_worker"
        )
        configured_plugins = settings.FTL_DOC_PROCESSING_PLUGINS

        for configured_plugin in configured_plugins:
            module = importlib.import_module(configured_plugin)
            classes = inspect.getmembers(
                module,
                lambda c:
                inspect.isclass(c)
                and issubclass(c, FTLDocProcessingBase)
                and c is not FTLDocProcessingBase
            )
            for name, classz in classes:
                self.plugins.append(classz())

    def apply_processing(self, ftl_doc):
        submit = self.executor.submit(self._handle, ftl_doc)
        submit.add_done_callback(self._callback)
        logger.info(f'{ftl_doc.pid} submitted to docs processing')

    def _handle(self, ftl_doc):
        # for each registered processing plugin, apply processing
        for plugin in self.plugins:
            try:
                logger.debug(f'Executing plugin {plugin.__class__.__name__} on {ftl_doc.pid}')
                plugin.process(ftl_doc)
            except:
                logger.exception(f'Error while processing {ftl_doc.pid} with plugin {plugin.__class__.__name__}')

        ftl_doc.tsvector = SEARCH_VECTOR
        ftl_doc.save()
        logger.info(f'{ftl_doc.pid} was processed correctly')

    def _callback(self, future):
        exception = future.exception()
        # never wait as this callback is called when the future is terminated
        if exception is not None:
            logger.error(f'One or more errors occurred during processing', exception)


class FTLDocProcessingBase:
    def process(self, ftl_doc):
        raise NotImplementedError
