"""
Database-agnostic Query Builder

Provides a fluent interface for constructing database queries that can be
translated to different database syntaxes (SQL, MongoDB, etc.).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ..config.logfire_config import search_logger
from .interfaces import IDatabase, QueryResult


class QueryType(Enum):
    """Types of database queries"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    COUNT = "COUNT"


class JoinType(Enum):
    """Types of JOIN operations"""
    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"
    CROSS = "CROSS"


class OrderDirection(Enum):
    """Sort order directions"""
    ASC = "ASC"
    DESC = "DESC"


class WhereOperator(Enum):
    """WHERE clause operators"""
    EQ = "="
    NEQ = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "IN"
    NOT_IN = "NOT IN"
    LIKE = "LIKE"
    ILIKE = "ILIKE"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"
    JSON_CONTAINS = "@>"
    JSON_CONTAINED_BY = "<@"


@dataclass
class WhereCondition:
    """Represents a WHERE clause condition"""
    column: str
    operator: WhereOperator
    value: Any
    connector: str = "AND"  # AND or OR
    
    def to_sql(self, param_index: int) -> Tuple[str, List[Any]]:
        """
        Convert to SQL with parameter binding
        
        Returns:
            Tuple of (SQL string, parameters list)
        """
        if self.operator in (WhereOperator.IS_NULL, WhereOperator.IS_NOT_NULL):
            return f"{self.column} {self.operator.value}", []
        elif self.operator == WhereOperator.IN:
            placeholders = ", ".join([f"${i}" for i in range(param_index, param_index + len(self.value))])
            return f"{self.column} IN ({placeholders})", list(self.value)
        elif self.operator == WhereOperator.BETWEEN:
            return f"{self.column} BETWEEN ${param_index} AND ${param_index + 1}", self.value
        else:
            return f"{self.column} {self.operator.value} ${param_index}", [self.value]


@dataclass
class WhereGroup:
    """Group of WHERE conditions with same connector"""
    conditions: List[Union[WhereCondition, 'WhereGroup']]
    connector: str = "AND"  # AND or OR
    
    def to_sql(self, param_index: int) -> Tuple[str, List[Any]]:
        """Convert group to SQL with parameter binding"""
        sql_parts = []
        params = []
        current_index = param_index
        
        for condition in self.conditions:
            sql_part, condition_params = condition.to_sql(current_index)
            sql_parts.append(sql_part)
            params.extend(condition_params)
            current_index += len(condition_params)
        
        joined = f" {self.connector} ".join(sql_parts)
        if len(self.conditions) > 1:
            joined = f"({joined})"
        
        return joined, params


@dataclass
class JoinClause:
    """Represents a JOIN clause"""
    join_type: JoinType
    table: str
    on_condition: str
    alias: Optional[str] = None
    
    def to_sql(self) -> str:
        """Convert to SQL"""
        table_ref = f"{self.table} AS {self.alias}" if self.alias else self.table
        return f"{self.join_type.value} JOIN {table_ref} ON {self.on_condition}"


@dataclass
class QueryBuilder:
    """
    Database-agnostic query builder with fluent interface
    """
    
    database: Optional[IDatabase] = None
    query_type: Optional[QueryType] = None
    table_name: Optional[str] = None
    table_alias: Optional[str] = None
    columns: List[str] = field(default_factory=lambda: ["*"])
    values: Union[Dict[str, Any], List[Dict[str, Any]]] = field(default_factory=dict)
    where_conditions: WhereGroup = field(default_factory=lambda: WhereGroup([]))
    join_clauses: List[JoinClause] = field(default_factory=list)
    group_by_columns: List[str] = field(default_factory=list)
    having_conditions: WhereGroup = field(default_factory=lambda: WhereGroup([]))
    order_by_clauses: List[Tuple[str, OrderDirection]] = field(default_factory=list)
    limit_value: Optional[int] = None
    offset_value: Optional[int] = None
    returning_columns: List[str] = field(default_factory=list)
    distinct: bool = False
    
    def reset(self) -> "QueryBuilder":
        """Reset the query builder to initial state"""
        self.__init__(self.database)
        return self
    
    def table(self, name: str, alias: Optional[str] = None) -> "QueryBuilder":
        """Set the table name and optional alias"""
        self.table_name = name
        self.table_alias = alias
        return self
    
    def select(self, *columns: str) -> "QueryBuilder":
        """
        Start a SELECT query
        
        Args:
            columns: Column names to select (default: "*")
        """
        self.query_type = QueryType.SELECT
        self.columns = list(columns) if columns else ["*"]
        return self
    
    def distinct_on(self, *columns: str) -> "QueryBuilder":
        """Add DISTINCT to SELECT query"""
        self.distinct = True
        if columns:
            self.columns = list(columns)
        return self
    
    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> "QueryBuilder":
        """
        Start an INSERT query
        
        Args:
            data: Record(s) to insert
        """
        self.query_type = QueryType.INSERT
        self.values = data if isinstance(data, list) else [data]
        return self
    
    def update(self, data: Dict[str, Any]) -> "QueryBuilder":
        """
        Start an UPDATE query
        
        Args:
            data: Fields to update
        """
        self.query_type = QueryType.UPDATE
        self.values = data
        return self
    
    def delete(self) -> "QueryBuilder":
        """Start a DELETE query"""
        self.query_type = QueryType.DELETE
        return self
    
    def count(self, column: str = "*") -> "QueryBuilder":
        """
        Start a COUNT query
        
        Args:
            column: Column to count (default: "*")
        """
        self.query_type = QueryType.COUNT
        self.columns = [f"COUNT({column}) as count"]
        return self
    
    def where(self, column: str, operator: Union[str, WhereOperator], value: Any = None) -> "QueryBuilder":
        """
        Add a WHERE condition
        
        Args:
            column: Column name
            operator: Comparison operator
            value: Value to compare (optional for IS NULL/IS NOT NULL)
        """
        if isinstance(operator, str):
            operator = WhereOperator(operator.upper())
        
        condition = WhereCondition(column, operator, value)
        self.where_conditions.conditions.append(condition)
        return self
    
    def or_where(self, column: str, operator: Union[str, WhereOperator], value: Any = None) -> "QueryBuilder":
        """Add an OR WHERE condition"""
        if isinstance(operator, str):
            operator = WhereOperator(operator.upper())
        
        condition = WhereCondition(column, operator, value, connector="OR")
        self.where_conditions.conditions.append(condition)
        return self
    
    def where_in(self, column: str, values: List[Any]) -> "QueryBuilder":
        """Add a WHERE IN condition"""
        return self.where(column, WhereOperator.IN, values)
    
    def where_not_in(self, column: str, values: List[Any]) -> "QueryBuilder":
        """Add a WHERE NOT IN condition"""
        return self.where(column, WhereOperator.NOT_IN, values)
    
    def where_null(self, column: str) -> "QueryBuilder":
        """Add a WHERE IS NULL condition"""
        return self.where(column, WhereOperator.IS_NULL)
    
    def where_not_null(self, column: str) -> "QueryBuilder":
        """Add a WHERE IS NOT NULL condition"""
        return self.where(column, WhereOperator.IS_NOT_NULL)
    
    def where_between(self, column: str, start: Any, end: Any) -> "QueryBuilder":
        """Add a WHERE BETWEEN condition"""
        return self.where(column, WhereOperator.BETWEEN, [start, end])
    
    def where_json(self, column: str, path: str, operator: Union[str, WhereOperator], value: Any) -> "QueryBuilder":
        """
        Add a WHERE condition for JSON fields
        
        Args:
            column: JSON column name
            path: JSON path (e.g., "$.address.city")
            operator: Comparison operator
            value: Value to compare
        """
        if isinstance(operator, str):
            operator = WhereOperator(operator.upper())
        
        # Format as JSON path query
        json_column = f"{column}->>{path}" if path else column
        return self.where(json_column, operator, value)
    
    def where_group(self, callback: callable) -> "QueryBuilder":
        """
        Add a grouped WHERE condition
        
        Args:
            callback: Function that receives a new QueryBuilder for the group
        """
        group_builder = QueryBuilder(self.database)
        callback(group_builder)
        
        if group_builder.where_conditions.conditions:
            group = WhereGroup(group_builder.where_conditions.conditions)
            self.where_conditions.conditions.append(group)
        
        return self
    
    def join(self, table: str, on: str, alias: Optional[str] = None) -> "QueryBuilder":
        """Add an INNER JOIN"""
        self.join_clauses.append(JoinClause(JoinType.INNER, table, on, alias))
        return self
    
    def left_join(self, table: str, on: str, alias: Optional[str] = None) -> "QueryBuilder":
        """Add a LEFT JOIN"""
        self.join_clauses.append(JoinClause(JoinType.LEFT, table, on, alias))
        return self
    
    def right_join(self, table: str, on: str, alias: Optional[str] = None) -> "QueryBuilder":
        """Add a RIGHT JOIN"""
        self.join_clauses.append(JoinClause(JoinType.RIGHT, table, on, alias))
        return self
    
    def full_join(self, table: str, on: str, alias: Optional[str] = None) -> "QueryBuilder":
        """Add a FULL OUTER JOIN"""
        self.join_clauses.append(JoinClause(JoinType.FULL, table, on, alias))
        return self
    
    def group_by(self, *columns: str) -> "QueryBuilder":
        """Add GROUP BY columns"""
        self.group_by_columns.extend(columns)
        return self
    
    def having(self, column: str, operator: Union[str, WhereOperator], value: Any) -> "QueryBuilder":
        """Add a HAVING condition"""
        if isinstance(operator, str):
            operator = WhereOperator(operator.upper())
        
        condition = WhereCondition(column, operator, value)
        self.having_conditions.conditions.append(condition)
        return self
    
    def order_by(self, column: str, direction: Union[str, OrderDirection] = OrderDirection.ASC) -> "QueryBuilder":
        """
        Add ORDER BY clause
        
        Args:
            column: Column to order by
            direction: Sort direction (ASC or DESC)
        """
        if isinstance(direction, str):
            direction = OrderDirection(direction.upper())
        
        self.order_by_clauses.append((column, direction))
        return self
    
    def limit(self, value: int) -> "QueryBuilder":
        """Set LIMIT value"""
        self.limit_value = value
        return self
    
    def offset(self, value: int) -> "QueryBuilder":
        """Set OFFSET value"""
        self.offset_value = value
        return self
    
    def paginate(self, page: int, per_page: int) -> "QueryBuilder":
        """
        Helper for pagination
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
        """
        self.limit_value = per_page
        self.offset_value = (page - 1) * per_page
        return self
    
    def returning(self, *columns: str) -> "QueryBuilder":
        """Add RETURNING clause for INSERT/UPDATE/DELETE"""
        self.returning_columns = list(columns) if columns else ["*"]
        return self
    
    def to_sql(self) -> Tuple[str, List[Any]]:
        """
        Build SQL query string with parameters
        
        Returns:
            Tuple of (SQL query string, parameters list)
        """
        if not self.query_type:
            raise ValueError("Query type not set")
        
        if not self.table_name:
            raise ValueError("Table name not set")
        
        if self.query_type == QueryType.SELECT or self.query_type == QueryType.COUNT:
            return self._build_select_query()
        elif self.query_type == QueryType.INSERT:
            return self._build_insert_query()
        elif self.query_type == QueryType.UPDATE:
            return self._build_update_query()
        elif self.query_type == QueryType.DELETE:
            return self._build_delete_query()
        else:
            raise ValueError(f"Unsupported query type: {self.query_type}")
    
    def _build_select_query(self) -> Tuple[str, List[Any]]:
        """Build SELECT query"""
        parts = []
        params = []
        param_index = 1
        
        # SELECT clause
        select_clause = "SELECT DISTINCT" if self.distinct else "SELECT"
        parts.append(f"{select_clause} {', '.join(self.columns)}")
        
        # FROM clause
        from_clause = f"FROM {self.table_name}"
        if self.table_alias:
            from_clause += f" AS {self.table_alias}"
        parts.append(from_clause)
        
        # JOIN clauses
        for join in self.join_clauses:
            parts.append(join.to_sql())
        
        # WHERE clause
        if self.where_conditions.conditions:
            where_sql, where_params = self.where_conditions.to_sql(param_index)
            parts.append(f"WHERE {where_sql}")
            params.extend(where_params)
            param_index += len(where_params)
        
        # GROUP BY clause
        if self.group_by_columns:
            parts.append(f"GROUP BY {', '.join(self.group_by_columns)}")
        
        # HAVING clause
        if self.having_conditions.conditions:
            having_sql, having_params = self.having_conditions.to_sql(param_index)
            parts.append(f"HAVING {having_sql}")
            params.extend(having_params)
            param_index += len(having_params)
        
        # ORDER BY clause
        if self.order_by_clauses:
            order_parts = [f"{col} {dir.value}" for col, dir in self.order_by_clauses]
            parts.append(f"ORDER BY {', '.join(order_parts)}")
        
        # LIMIT and OFFSET
        if self.limit_value is not None:
            parts.append(f"LIMIT {self.limit_value}")
        if self.offset_value is not None:
            parts.append(f"OFFSET {self.offset_value}")
        
        return " ".join(parts), params
    
    def _build_insert_query(self) -> Tuple[str, List[Any]]:
        """Build INSERT query"""
        if not self.values:
            raise ValueError("No data to insert")
        
        # Ensure values is a list
        records = self.values if isinstance(self.values, list) else [self.values]
        
        # Get column names from first record
        columns = list(records[0].keys())
        
        # Build VALUES clause with parameter placeholders
        params = []
        value_groups = []
        param_index = 1
        
        for record in records:
            placeholders = []
            for col in columns:
                placeholders.append(f"${param_index}")
                params.append(record.get(col))
                param_index += 1
            value_groups.append(f"({', '.join(placeholders)})")
        
        # Build query
        query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES {', '.join(value_groups)}"
        
        # Add RETURNING clause if specified
        if self.returning_columns:
            query += f" RETURNING {', '.join(self.returning_columns)}"
        
        return query, params
    
    def _build_update_query(self) -> Tuple[str, List[Any]]:
        """Build UPDATE query"""
        if not self.values:
            raise ValueError("No data to update")
        
        parts = [f"UPDATE {self.table_name}"]
        params = []
        param_index = 1
        
        # SET clause
        set_parts = []
        for column, value in self.values.items():
            set_parts.append(f"{column} = ${param_index}")
            params.append(value)
            param_index += 1
        parts.append(f"SET {', '.join(set_parts)}")
        
        # WHERE clause
        if self.where_conditions.conditions:
            where_sql, where_params = self.where_conditions.to_sql(param_index)
            parts.append(f"WHERE {where_sql}")
            params.extend(where_params)
        else:
            search_logger.warning("UPDATE query without WHERE clause - this will update all records!")
        
        # RETURNING clause
        if self.returning_columns:
            parts.append(f"RETURNING {', '.join(self.returning_columns)}")
        
        return " ".join(parts), params
    
    def _build_delete_query(self) -> Tuple[str, List[Any]]:
        """Build DELETE query"""
        parts = [f"DELETE FROM {self.table_name}"]
        params = []
        param_index = 1
        
        # WHERE clause
        if self.where_conditions.conditions:
            where_sql, where_params = self.where_conditions.to_sql(param_index)
            parts.append(f"WHERE {where_sql}")
            params.extend(where_params)
        else:
            search_logger.warning("DELETE query without WHERE clause - this will delete all records!")
        
        # RETURNING clause
        if self.returning_columns:
            parts.append(f"RETURNING {', '.join(self.returning_columns)}")
        
        return " ".join(parts), params
    
    async def execute(self) -> QueryResult:
        """
        Execute the built query
        
        Returns:
            QueryResult with query results
        """
        if not self.database:
            raise ValueError("Database connection not set")
        
        sql, params = self.to_sql()
        
        # Log the query for debugging
        search_logger.debug(f"Executing query: {sql}")
        search_logger.debug(f"Parameters: {params}")
        
        # Execute based on query type
        if self.query_type == QueryType.SELECT or self.query_type == QueryType.COUNT:
            return await self.database.select(
                self.table_name,
                columns=self.columns,
                filters=self._extract_simple_filters(),
                order_by=self._format_order_by(),
                limit=self.limit_value,
                offset=self.offset_value
            )
        elif self.query_type == QueryType.INSERT:
            return await self.database.insert(
                self.table_name,
                self.values,
                returning=self.returning_columns if self.returning_columns else None
            )
        elif self.query_type == QueryType.UPDATE:
            return await self.database.update(
                self.table_name,
                self.values,
                self._extract_simple_filters(),
                returning=self.returning_columns if self.returning_columns else None
            )
        elif self.query_type == QueryType.DELETE:
            return await self.database.delete(
                self.table_name,
                self._extract_simple_filters(),
                returning=self.returning_columns if self.returning_columns else None
            )
        else:
            # Fallback to raw SQL execution
            return await self.database.execute(sql, {"params": params})
    
    def _extract_simple_filters(self) -> Dict[str, Any]:
        """Extract simple equality filters for basic database methods"""
        filters = {}
        for condition in self.where_conditions.conditions:
            if isinstance(condition, WhereCondition) and condition.operator == WhereOperator.EQ:
                filters[condition.column] = condition.value
        return filters
    
    def _format_order_by(self) -> Optional[str]:
        """Format ORDER BY clause for database methods"""
        if not self.order_by_clauses:
            return None
        
        parts = []
        for column, direction in self.order_by_clauses:
            parts.append(f"{column} {direction.value}")
        
        return ", ".join(parts)


def query(database: Optional[IDatabase] = None) -> QueryBuilder:
    """
    Create a new QueryBuilder instance
    
    Args:
        database: Optional database connection for execution
        
    Returns:
        New QueryBuilder instance
    """
    return QueryBuilder(database=database)