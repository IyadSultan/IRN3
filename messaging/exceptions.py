class MessageError(Exception):
    """Base exception class for messaging app errors"""
    pass

class RecipientError(MessageError):
    """Exception raised for errors related to message recipients"""
    pass

class AttachmentError(MessageError):
    """Exception raised for errors related to message attachments"""
    pass

class ThreadError(MessageError):
    """Exception raised for errors related to message threading"""
    pass 