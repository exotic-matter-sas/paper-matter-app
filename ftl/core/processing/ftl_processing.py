import logging
from concurrent.futures.thread import ThreadPoolExecutor
from pydoc import locate

logger = logging.getLogger(__name__)


class FTLDocumentProcessing:
    """
    A base document processing class, to be used for adding processing to document such as OCR,
    text extraction, etc.
    """
    executor = None
    plugins = list()

    def __init__(self, configured_plugins, max_workers=1):
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ftl_doc_processing_worker"
        )

        for configured_plugin in configured_plugins:
            my_class = locate(configured_plugin)

            if issubclass(my_class, FTLDocProcessingBase) and my_class is not FTLDocProcessingBase:
                self.plugins.append(my_class())

    def apply_processing(self, ftl_doc):
        submit = self.executor.submit(self._handle, ftl_doc)
        submit.add_done_callback(self._callback)
        logger.info(f'{ftl_doc.pid} submitted to docs processing')
        return submit

    def _handle(self, ftl_doc):
        # for each registered processing plugin, apply processing
        for plugin in self.plugins:
            try:
                logger.debug(f'Executing plugin {plugin.__class__.__name__} on {ftl_doc.pid}')
                plugin.process(ftl_doc)
            except:
                logger.exception(f'Error while processing {ftl_doc.pid} with plugin {plugin.__class__.__name__}')

        logger.info(f'{ftl_doc.pid} was processed correctly')

    def _callback(self, future):
        exception = future.exception()
        # never wait as this callback is called when the future is terminated
        if exception is not None:
            logger.error(f'One or more errors occurred during processing', exception)


class FTLDocProcessingBase:
    def process(self, ftl_doc):
        raise NotImplementedError
