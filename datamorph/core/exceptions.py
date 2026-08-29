"""
DataMorph Studio - Exception Hierarchy
Defines comprehensive domain-specific exceptions for the data preprocessing platform.
"""

class DataMorphError(Exception):
    """Base exception for all DataMorph runtime errors."""
    def __init__(self, message: str, error_code: str = "ERR_GENERIC", details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self):
        return {
            "error": self.__class__.__name__,
            "code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class SchemaValidationError(DataMorphError):
    """Raised when data schema validation fails against expected definitions."""
    def __init__(self, message: str, column_name: str = None, expected_type: str = None, actual_type: str = None):
        details = {
            "column": column_name,
            "expected_type": expected_type,
            "actual_type": actual_type
        }
        super().__init__(message, error_code="ERR_SCHEMA_VALIDATION", details=details)


class TransformerError(DataMorphError):
    """Raised when a transformer operation fails during fit or transform phase."""
    def __init__(self, message: str, transformer_name: str = None, column: str = None):
        details = {
            "transformer": transformer_name,
            "column": column
        }
        super().__init__(message, error_code="ERR_TRANSFORMER_EXECUTION", details=details)


class TransformerNotFittedError(TransformerError):
    """Raised when transform() is called on an unfitted transformer."""
    def __init__(self, transformer_name: str):
        super().__init__(
            f"Transformer '{transformer_name}' is not fitted yet. Call 'fit()' or 'fit_transform()' before 'transform()'.",
            transformer_name=transformer_name
        )
        self.error_code = "ERR_NOT_FITTED"


class PipelineExecutionError(DataMorphError):
    """Raised when pipeline graph compilation or node execution encounters a fatal error."""
    def __init__(self, message: str, step_id: str = None, pipeline_id: str = None):
        details = {
            "step_id": step_id,
            "pipeline_id": pipeline_id
        }
        super().__init__(message, error_code="ERR_PIPELINE_EXECUTION", details=details)


class DatasetStorageError(DataMorphError):
    """Raised during dataset I/O or repository persistence failures."""
    def __init__(self, message: str, filepath: str = None):
        details = {"filepath": filepath}
        super().__init__(message, error_code="ERR_STORAGE_IO", details=details)


class DataDriftError(DataMorphError):
    """Raised when drift calculation encounters numerical instability or mismatched schemas."""
    def __init__(self, message: str, feature_name: str = None):
        details = {"feature_name": feature_name}
        super().__init__(message, error_code="ERR_DRIFT_COMPUTATION", details=details)


class AuthenticationError(DataMorphError):
    """Raised when user authentication or token verification fails."""
    def __init__(self, message: str = "Invalid credentials or session expired"):
        super().__init__(message, error_code="ERR_AUTH_FAILED")


class AuthorizationError(DataMorphError):
    """Raised when user lacks permission for the requested resource."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, error_code="ERR_PERMISSION_DENIED")
