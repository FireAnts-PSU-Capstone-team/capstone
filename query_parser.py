import json

db_tables = ['intake', 'txn_history', 'archive', 'metadata']


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
    if op == '<':
        pass
    elif op == '>':
        pass
    elif op == '=':
        pass
    else:
        raise RequestParseException(unknown_operator_msg(op))


def build_query(q):
    try:
        # table name required
        table = q.get('table')
        if table not in db_tables:
            raise RequestParseException(invalid_table_msg(table))

        col_names = []
        if table == 'intake':
            from models import IntakeRow
            col_names = [x.name.lower() for x in IntakeRow.ColNames]

        # if columns not listed, assume all
        columns = q.get('columns', '*')
        if columns != '*':
            for col in columns:
                if col.lower() not in col_names:
                    raise RequestParseException(invalid_column_msg(col))

        query = f"SELECT {','.join(columns)} FROM {table} "
        # get extended filtering
        where = q.get('where')
        if where is not None:
            query += 'WHERE '
            # iterate over operators
            query += parse_op(where)

        return query + ';'

    except RequestParseException as e:
        return invalid_request_msg(e.msg)


if __name__ == '__main__':
    with open('resources/test-query-fail-1.json', 'r') as f:
        body = json.load(f)
    q = build_query(body)
    print(q)

