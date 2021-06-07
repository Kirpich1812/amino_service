from prettytable import PrettyTable


def create_table(title: str, rows: list):
    table = PrettyTable()
    table.field_names = ["№", "Action"]
    table.add_rows(rows)
    return table.get_string(title=title)
