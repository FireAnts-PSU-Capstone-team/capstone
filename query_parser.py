import json


class RequestParseException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


def invalid_column_msg(c: str) -> str:
    return f"Column {c} not in known list"


def invalid_table_msg(t: str) -> str:
    return f"Table {t} does not match known list"


def unknown_operator_msg(o: str) -> str:
    return f"Encountered an unrecognized operator ({o})"


def invalid_request_msg(e: str) -> str:
    return f"Request has invalid structure. Error: {e}"


def invalid_binary_operation(o: str) -> str:
    return f"Found an AND or OR construct with invalid structure. Construct was: {json.dumps(o)}"


class QueryParser:

    def __init__(self, tables: [str]):
        self.db_tables = tables
        self.col_names = []

    def parse_or(self, op_block: json) -> str:
        """
        Parses an OR-block in a request.
        Args:
            op_block ({}): JSON block containing an OR operation
        Returns (str): the SQL query string corresponding to the JSON request
        Raises: RequestParseException if op cannot be parsed
        """
        or_block = op_block.get('or')
        try:
            if len(or_block) != 2:
                raise IndexError
            left = or_block[0]
            right = or_block[1]
            return f"({self.parse_op(left)} OR {self.parse_op(right)})"
        except IndexError:
            raise RequestParseException(invalid_binary_operation(op_block))

    def parse_and(self, op_block: json) -> str:
        """
        Parses an AND-block in a request.
        Args:
            op_block ({}): JSON block containing an AND operation
        Returns (str): the SQL query string corresponding to the JSON request
        Raises: RequestParseException if op cannot be parsed
        """
        and_block = op_block.get('and')
        try:
            if len(and_block) != 2:
                raise IndexError
            left = and_block[0]
            right = and_block[1]
            return f"({self.parse_op(left)} AND {self.parse_op(right)})"
        except IndexError:
            raise RequestParseException(invalid_binary_operation(op_block))

    def parse_op(self, op_block: json) -> str:
        """
        Parses an operation in a request.
        Args:
            op_block ({}): JSON block containing the operation
        Returns (str): the SQL query string corresponding to the JSON request
        Raises: RequestParseException if op cannot be parsed
        """
        if op_block.get('and') is not None and op_block.get('or') is not None:
            raise RequestParseException(invalid_request_msg(op_block))
        if op_block.get('and') is not None:
            return self.parse_and(op_block)
        if op_block.get('or') is not None:
            return self.parse_or(op_block)
        # basic operator
        op = op_block.get('op')
        if op is None:
            raise RequestParseException("No operation requested in block: " + json.dumps(op_block))
        if op in ['<', '<=', '>', '>=', '=']:
            col = op_block.get('column')
            self.validate_column(col)
            operand = op_block.get('operand')
            return f"({col} {op} '{operand}')"
        else:
            raise RequestParseException(unknown_operator_msg(op))

    def validate_column(self, col: str) -> None:
        """
        Raises an exception if the given column is not in the approved list.
        Args:
            col (str): column name
        Returns: None
        Raises: RequestParseException if col is not a valid column name
        """
        if col.lower() not in self.col_names:
            raise RequestParseException(invalid_column_msg(col))

    def build_query(self, q: json) -> str:
        """
        Constructs a SQL query from a JSON input.
        Args:
            q ({}): JSON query input
        Returns (str): the SQL query string
        """
        try:
            # table name required
            table = q.get('table')
            if table is None:
                raise RequestParseException("No table named in request")
            elif table not in self.db_tables:
                raise RequestParseException(invalid_table_msg(table))

            if table == 'intake':
                from models import IntakeRow
                self.col_names = [x.name.lower() for x in IntakeRow.ColNames]
            # TODO: uncomment once other tables have ColNames classes
            # elif table == 'archive':
            #     from models import ArchiveRow
            #     self.col_names = [x.name.lower() for x in ArchiveRow.ColNames]
            # elif table == 'metadata':
            #     from models import MetadataRow
            #     self.col_names = [x.name.lower() for x in MetadataRow.ColNames]
            # elif table == 'txn_history':
            #     from models import TxnHistoryRow
            #     self.col_names = [x.name.lower() for x in TxnHistoryRow.ColNames]
            else:
                raise RequestParseException("Requested table not found")

            # if columns not listed, assume all
            columns = q.get('columns')
            if columns is None:
                columns = '*'
            elif not isinstance(columns, list):
                raise RequestParseException("Columns must be present as list in request body")
            if columns != '*':
                for col in columns:
                    self.validate_column(col)

            query = f"SELECT {', '.join(columns)} FROM {table} "
            # get extended filtering
            where = q.get('where')
            if where is not None:
                query += 'WHERE '
                # iterate over operators
                query += self.parse_op(where)

            return query + ';'

        except RequestParseException as e:
            e.msg = invalid_request_msg(e.msg)
            raise e
