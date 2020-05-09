import json


class RequestParseException(Exception):
    def __init__(self, msg):
        self.msg = msg


def invalid_column_msg(c):
    return f"Column {c} not in known list"


def invalid_table_msg(t):
    return f"Table {t} does not match known list"


def unknown_operator_msg(o):
    return f"Encountered an unrecognized operator ({o})"


def invalid_request_msg(e):
    return f"Request has invalid structure. Error: {e}"


def invalid_binary_operation(o):
    return f"Found an AND or OR construct with invalid structure. Construct was: {json.dumps(o)}"


class QueryParser:
    # TODO: get this from elsewhere, bad practice to maintain separate lists
    db_tables = ['intake', 'txn_history', 'archive', 'metadata']

    def parse_or(self, op_block):
        or_block = op_block.get('or')
        try:
            if len(or_block) != 2:
                raise IndexError
            left = or_block[0]
            right = or_block[1]
            return f"({self.parse_op(left)} OR {self.parse_op(right)})"
        except IndexError:
            raise RequestParseException(invalid_binary_operation(op_block))

    def parse_and(self, op_block):
        and_block = op_block.get('and')
        try:
            if len(and_block) != 2:
                raise IndexError
            left = and_block[0]
            right = and_block[1]
            return f"({self.parse_op(left)} AND {self.parse_op(right)})"
        except IndexError:
            raise RequestParseException(invalid_binary_operation(op_block))

    def parse_op(self, op_block):
        if op_block.get('and') is not None:
            return self.parse_and(op_block)
        if op_block.get('or') is not None:
            return self.parse_or(op_block)
        # basic operator
        op = op_block.get('op')
        if op in ['<', '>', '=']:
            col = op_block.get('column')
            self.validate_column(col)
            operand = op_block.get('operand')
            # TODO: this is a breaking problem since we're quoting everything
            #       need to account for numeric/null values, and
            #       refactor to  construct a prepared statement instead of building this way
            return f"({col} {op} '{operand}')"
        else:
            raise RequestParseException(unknown_operator_msg(op))

    def validate_column(self, col):
        if col.lower() not in self.col_names:
            raise RequestParseException(invalid_column_msg(col))

    def build_query(self, q: json):
        try:
            # table name required
            table = q.get('table')
            if table not in self.db_tables:
                raise RequestParseException(invalid_table_msg(table))

            if table == 'intake':
                from models import IntakeRow
                self.col_names = [x.name.lower() for x in IntakeRow.ColNames]
            # TODO: add support for other tables here
            # elif table == 'archive':
            #     from models import ArchiveRow
            #     self.col_names = [x.name.lower() for x in ArchiveRow.ColNames]
            # elif table == 'metadata':
            #     pass
            # elif table == 'txn_history':
            #     pass

            # if columns not listed, assume all
            columns = q.get('columns', '*')
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
            return invalid_request_msg(e.msg)


if __name__ == '__main__':
    with open('resources/test-query-or-1.json', 'r') as f:
        body = json.load(f)
    qp = QueryParser()
    q = qp.build_query(body)
    print(q)
