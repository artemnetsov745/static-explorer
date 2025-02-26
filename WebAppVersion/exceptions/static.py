class BaseStaticFilesTraversalServiceException(Exception):
    """ Base exception for all exceptions raised by StaticFilesTraversalService. """


class FailedToDownloadFileException(BaseStaticFilesTraversalServiceException):
    """ Exception raised when an attempt is made to download a file. """