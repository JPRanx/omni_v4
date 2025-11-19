"""
Order Data Transfer Object.

Represents a single order with categorization and fulfillment metrics.
Used for efficiency analysis and timeslot grading.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from src.core.result import Result
from src.core.errors import ValidationError


@dataclass(frozen=True)
class OrderDTO:
    """
    Immutable data transfer object for a single order.

    Combines data from multiple Toast CSV sources:
    - OrderDetails: Order #, total duration, table
    - Kitchen Details: Fulfillment time, server, table
    - EOD: Cash drawer, dining option
    - TimeEntries: Server/employee positions

    Attributes:
        check_number: Unique order identifier (from Kitchen/OrderDetails/EOD)
        category: Order type (Lobby/Drive-Thru/ToGo/Unknown)
        fulfillment_minutes: Kitchen fulfillment time in minutes (from Kitchen Details)
        order_duration_minutes: Total order duration in minutes (from OrderDetails)
        order_time: When order was opened (from OrderDetails 'Opened')
        server: Server/employee name (from Kitchen Details or OrderDetails)
        shift: Shift when order was placed (morning/evening)
        table: Table number if dine-in (from Kitchen/OrderDetails/EOD)
        cash_drawer: Cash drawer used (from EOD, helps identify Drive-Thru)
        dining_option: Dining option from EOD (Dine In/ToGo/etc)
        employee_position: Job title of server (from TimeEntries, helps categorization)
        expediter_level: Kitchen expedition level (1=kitchen done, 2=server pickup)
        metadata: Additional context for debugging
    """

    check_number: str
    category: str  # Lobby, Drive-Thru, ToGo, Unknown
    fulfillment_minutes: float
    order_duration_minutes: Optional[float]
    order_time: datetime
    server: str
    shift: str  # morning, evening
    table: Optional[str] = None
    cash_drawer: Optional[str] = None
    dining_option: Optional[str] = None
    employee_position: Optional[str] = None
    expediter_level: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    @staticmethod
    def create(
        check_number: str,
        category: str,
        fulfillment_minutes: float,
        order_duration_minutes: Optional[float],
        order_time: datetime,
        server: str,
        shift: str,
        table: Optional[str] = None,
        cash_drawer: Optional[str] = None,
        dining_option: Optional[str] = None,
        employee_position: Optional[str] = None,
        expediter_level: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Result['OrderDTO']:
        """
        Create OrderDTO with validation.

        Args:
            check_number: Order identifier (must be non-empty)
            category: Order category (must be valid category)
            fulfillment_minutes: Fulfillment time (must be non-negative)
            order_duration_minutes: Total order duration (if present, must be non-negative)
            order_time: Order timestamp (must be datetime)
            server: Server name (must be non-empty)
            shift: Shift identifier (must be non-empty)
            table: Optional table number
            cash_drawer: Optional cash drawer identifier
            dining_option: Optional dining option
            employee_position: Optional job title
            expediter_level: Optional expediter level (1 or 2)
            metadata: Optional additional context

        Returns:
            Result[OrderDTO]: Created DTO or validation error
        """
        # Validate check_number
        if not check_number or not check_number.strip():
            return Result.fail(
                ValidationError(
                    "check_number cannot be empty",
                    context={'check_number': check_number}
                )
            )

        # Validate category
        valid_categories = {'Lobby', 'Drive-Thru', 'ToGo', 'Unknown'}
        if category not in valid_categories:
            return Result.fail(
                ValidationError(
                    f"Invalid category: {category}. Must be one of {valid_categories}",
                    context={'category': category, 'valid': list(valid_categories)}
                )
            )

        # Validate fulfillment_minutes
        if fulfillment_minutes < 0:
            return Result.fail(
                ValidationError(
                    "fulfillment_minutes must be non-negative",
                    context={'fulfillment_minutes': fulfillment_minutes}
                )
            )

        # Validate order_duration_minutes if present
        if order_duration_minutes is not None and order_duration_minutes < 0:
            return Result.fail(
                ValidationError(
                    "order_duration_minutes must be non-negative",
                    context={'order_duration_minutes': order_duration_minutes}
                )
            )

        # Validate order_time is datetime
        if not isinstance(order_time, datetime):
            return Result.fail(
                ValidationError(
                    "order_time must be a datetime object",
                    context={'order_time': type(order_time).__name__}
                )
            )

        # Validate server
        if not server or not server.strip():
            return Result.fail(
                ValidationError(
                    "server cannot be empty",
                    context={'server': server}
                )
            )

        # Validate shift
        valid_shifts = {'morning', 'evening'}
        if shift not in valid_shifts:
            return Result.fail(
                ValidationError(
                    f"Invalid shift: {shift}. Must be 'morning' or 'evening'",
                    context={'shift': shift, 'valid': list(valid_shifts)}
                )
            )

        # Validate expediter_level if present
        if expediter_level is not None and expediter_level not in {1, 2}:
            return Result.fail(
                ValidationError(
                    "expediter_level must be 1 or 2",
                    context={'expediter_level': expediter_level}
                )
            )

        # Create DTO
        try:
            order = OrderDTO(
                check_number=check_number.strip(),
                category=category,
                fulfillment_minutes=fulfillment_minutes,
                order_duration_minutes=order_duration_minutes,
                order_time=order_time,
                server=server.strip(),
                shift=shift,
                table=table.strip() if table else None,
                cash_drawer=cash_drawer.strip() if cash_drawer else None,
                dining_option=dining_option.strip() if dining_option else None,
                employee_position=employee_position.strip() if employee_position else None,
                expediter_level=expediter_level,
                metadata=metadata or {}
            )
            return Result.ok(order)
        except Exception as e:
            return Result.fail(
                ValidationError(
                    f"Failed to create OrderDTO: {str(e)}",
                    context={'error': str(e)}
                )
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize OrderDTO to dictionary.

        Returns:
            dict: Dictionary representation
        """
        return {
            'check_number': self.check_number,
            'category': self.category,
            'fulfillment_minutes': self.fulfillment_minutes,
            'order_duration_minutes': self.order_duration_minutes,
            'order_time': self.order_time.isoformat(),
            'server': self.server,
            'shift': self.shift,
            'table': self.table,
            'cash_drawer': self.cash_drawer,
            'dining_option': self.dining_option,
            'employee_position': self.employee_position,
            'expediter_level': self.expediter_level,
            'metadata': self.metadata
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Result['OrderDTO']:
        """
        Deserialize OrderDTO from dictionary.

        Args:
            data: Dictionary with OrderDTO fields

        Returns:
            Result[OrderDTO]: Deserialized DTO or error
        """
        try:
            # Parse order_time from ISO format
            order_time = datetime.fromisoformat(data['order_time'])

            return OrderDTO.create(
                check_number=data['check_number'],
                category=data['category'],
                fulfillment_minutes=data['fulfillment_minutes'],
                order_duration_minutes=data.get('order_duration_minutes'),
                order_time=order_time,
                server=data['server'],
                shift=data['shift'],
                table=data.get('table'),
                cash_drawer=data.get('cash_drawer'),
                dining_option=data.get('dining_option'),
                employee_position=data.get('employee_position'),
                expediter_level=data.get('expediter_level'),
                metadata=data.get('metadata')
            )
        except KeyError as e:
            return Result.fail(
                ValidationError(
                    f"Missing required field: {str(e)}",
                    context={'data': data}
                )
            )
        except Exception as e:
            return Result.fail(
                ValidationError(
                    f"Failed to deserialize OrderDTO: {str(e)}",
                    context={'error': str(e), 'data': data}
                )
            )

    def is_dine_in(self) -> bool:
        """Check if order is dine-in (Lobby)."""
        return self.category == 'Lobby'

    def is_drive_thru(self) -> bool:
        """Check if order is drive-through."""
        return self.category == 'Drive-Thru'

    def is_togo(self) -> bool:
        """Check if order is to-go."""
        return self.category == 'ToGo'

    def has_table(self) -> bool:
        """Check if order has a table assigned."""
        return self.table is not None and self.table.strip() != ''

    def __repr__(self) -> str:
        return (
            f"OrderDTO(check={self.check_number}, category={self.category}, "
            f"fulfillment={self.fulfillment_minutes:.1f}min, shift={self.shift})"
        )
