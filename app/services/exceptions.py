class PDFMergeException(Exception):
    pass


class InvalidPINException(PDFMergeException):
    pass


class InvalidDocumentCombination(PDFMergeException):
    pass

class NoAggrNotFoundException(Exception):
    pass