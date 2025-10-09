"""
Custom Exceptions
애플리케이션 전용 예외 클래스
"""


# ===== Base Exception =====
class RoboStockException(Exception):
    """모든 RoboStock 예외의 베이스 클래스"""

    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


# ===== Domain Exceptions =====
class DomainException(RoboStockException):
    """도메인 계층 예외"""
    pass


class InvalidBlockCriteriaException(DomainException):
    """블록 탐지 조건이 유효하지 않을 때"""

    def __init__(self, criteria: str, reason: str):
        super().__init__(
            f"Invalid block criteria '{criteria}': {reason}",
            code="INVALID_BLOCK_CRITERIA"
        )


class InvalidDateRangeException(DomainException):
    """날짜 범위가 유효하지 않을 때"""

    def __init__(self, start_date, end_date):
        super().__init__(
            f"Invalid date range: start={start_date}, end={end_date}",
            code="INVALID_DATE_RANGE"
        )


class InvalidPriceDataException(DomainException):
    """주가 데이터가 유효하지 않을 때"""

    def __init__(self, stock_code: str, reason: str):
        super().__init__(
            f"Invalid price data for {stock_code}: {reason}",
            code="INVALID_PRICE_DATA"
        )


# ===== Repository Exceptions =====
class RepositoryException(RoboStockException):
    """Repository 계층 예외"""
    pass


class EntityNotFoundException(RepositoryException):
    """엔티티를 찾을 수 없을 때"""

    def __init__(self, entity_type: str, identifier: str):
        super().__init__(
            f"{entity_type} not found: {identifier}",
            code="ENTITY_NOT_FOUND"
        )


class DuplicateEntityException(RepositoryException):
    """중복된 엔티티가 존재할 때"""

    def __init__(self, entity_type: str, identifier: str):
        super().__init__(
            f"Duplicate {entity_type}: {identifier}",
            code="DUPLICATE_ENTITY"
        )


class DatabaseConnectionException(RepositoryException):
    """데이터베이스 연결 실패"""

    def __init__(self, reason: str):
        super().__init__(
            f"Database connection failed: {reason}",
            code="DB_CONNECTION_FAILED"
        )


# ===== Service Exceptions =====
class ServiceException(RoboStockException):
    """서비스 계층 예외"""
    pass


class DataCollectionException(ServiceException):
    """데이터 수집 실패"""

    def __init__(self, stock_code: str, reason: str):
        super().__init__(
            f"Data collection failed for {stock_code}: {reason}",
            code="DATA_COLLECTION_FAILED"
        )


class BlockDetectionException(ServiceException):
    """블록 탐지 실패"""

    def __init__(self, stock_code: str, reason: str):
        super().__init__(
            f"Block detection failed for {stock_code}: {reason}",
            code="BLOCK_DETECTION_FAILED"
        )


class AnalysisException(ServiceException):
    """분석 실패"""

    def __init__(self, case_id: int, reason: str):
        super().__init__(
            f"Analysis failed for case {case_id}: {reason}",
            code="ANALYSIS_FAILED"
        )


# ===== External API Exceptions =====
class ExternalAPIException(RoboStockException):
    """외부 API 호출 예외"""
    pass


class PykrxAPIException(ExternalAPIException):
    """pykrx API 호출 실패"""

    def __init__(self, endpoint: str, reason: str):
        super().__init__(
            f"Pykrx API call failed [{endpoint}]: {reason}",
            code="PYKRX_API_FAILED"
        )


class APIRateLimitException(ExternalAPIException):
    """API 호출 제한 초과"""

    def __init__(self, api_name: str, retry_after: int = None):
        message = f"API rate limit exceeded: {api_name}"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        super().__init__(message, code="API_RATE_LIMIT")


class APITimeoutException(ExternalAPIException):
    """API 타임아웃"""

    def __init__(self, api_name: str, timeout: int):
        super().__init__(
            f"API timeout: {api_name} ({timeout}s)",
            code="API_TIMEOUT"
        )


# ===== Validation Exceptions =====
class ValidationException(RoboStockException):
    """유효성 검증 실패"""

    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Validation failed for '{field}': {reason}",
            code="VALIDATION_FAILED"
        )


class InvalidStockCodeException(ValidationException):
    """유효하지 않은 종목 코드"""

    def __init__(self, stock_code: str):
        super().__init__(
            "stock_code",
            f"Invalid stock code format: {stock_code}"
        )


class InvalidMarketTypeException(ValidationException):
    """유효하지 않은 시장 타입"""

    def __init__(self, market_type: str):
        super().__init__(
            "market_type",
            f"Invalid market type: {market_type}"
        )


# ===== Configuration Exceptions =====
class ConfigurationException(RoboStockException):
    """설정 오류"""

    def __init__(self, config_key: str, reason: str):
        super().__init__(
            f"Configuration error [{config_key}]: {reason}",
            code="CONFIGURATION_ERROR"
        )


# ===== Business Logic Exceptions =====
class BusinessRuleException(RoboStockException):
    """비즈니스 규칙 위반"""

    def __init__(self, rule: str, reason: str):
        super().__init__(
            f"Business rule violated [{rule}]: {reason}",
            code="BUSINESS_RULE_VIOLATED"
        )


class InsufficientDataException(BusinessRuleException):
    """데이터 부족"""

    def __init__(self, required_days: int, actual_days: int):
        super().__init__(
            "minimum_data_requirement",
            f"Required {required_days} days, got {actual_days} days"
        )


class NoBlockFoundException(BusinessRuleException):
    """블록을 찾을 수 없음"""

    def __init__(self, stock_code: str, block_type: str):
        super().__init__(
            "block_detection",
            f"No {block_type} block found for {stock_code}"
        )
