import json
from models import IntakeRow

db_tables = ['intake', 'txn_history', 'archive', 'metadata']
col_names = [x.name.lower() for x in IntakeRow.ColNames]


def invalid_request_msg(e):
    return f"Request has invalid structure. Error: {e}"


def unknown_operator_msg(o):
    return f"Encountered an unrecognized operator ({o})"


def invalid_table_msg(t):
    return f"Table {t} does not match known list"


def invalid_column_msg(c):
    return f"Column {c} not in known list"


class RequestParseException(Exception):
    def __init__(self, msg):
        self.msg = msg


def parse_or(or_block):
    return "or"


def parse_and(and_block):
    return "and"


def parse_op(op_block):
    if op_block.get('and') is not None:
        return parse_and(op_block.get('and'))
    if op_block.get('or') is not None:
        return parse_or(op_block.get('or'))
    # basic operator
    op = op_block.get('op')
    if op in ['<', '>', '=']:
        col = op_block.get('column')
        validate_column(col)
        operand = op_block.get('operand')
        # TODO: this is going to be a problem since we're quoting everything
        # TODO: need to account for numeric/null values
        return f" {col} {op} '{operand}'"
    else:
        raise RequestParseException(unknown_operator_msg(op))


def validate_column(col):
    if col.lower() not in col_names:
        raise RequestParseException(invalid_column_msg(col))


def build_query(q):
    try:
        # table name required
        table = q.get('table')
        if table not in db_tables:
            raise RequestParseException(invalid_table_msg(table))

        # col_names = []
        # if table == 'intake':
            # from models import IntakeRow
            # TODO: transition to class, use this to set instance col_names
            # col_names = [x.name.lower() for x in IntakeRow.ColNames]

        # if columns not listed, assume all
        columns = q.get('columns', '*')
        if columns != '*':
            for col in columns:
                validate_column(col)

        query = f"SELECT {','.join(columns)} FROM {table} "
        # get extended filtering
        where = q.get('where')
        if where is not None:
            query += 'WHERE'
            # iterate over operators
            query += parse_op(where)

        return query + ';'

    except RequestParseException as e:
        return invalid_request_msg(e.msg)


if __name__ == '__main__':
    with open('resources/test-query-equals.json', 'r') as f:
        body = json.load(f)
    q = build_query(body)
    print(q)

