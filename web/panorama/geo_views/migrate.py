from django.db.migrations.operations.base import Operation


view_history = dict()


class ManageView(Operation):

    reversible = True

    def __init__(self, view_name, sql):
        super().__init__()
        self.view_name = view_name
        self.sql = sql

    def push_history(self, app_label):
        view_name = '{}-{}'.format(app_label, self.view_name)
        view_history.setdefault(view_name, []).append(self.sql)

    def pop_previous_sql(self, app_label):
        view_name = '{}-{}'.format(app_label, self.view_name)
        history = view_history.get(view_name)
        if not history:
            return None

        history.pop()
        if not history:
            return None

        history.pop()
        if not history:
            return None

        return history[-1]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("DROP VIEW IF EXISTS {}".format(self.view_name))
        schema_editor.execute("CREATE VIEW {} AS {}".format(self.view_name, self.sql))

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("DROP VIEW IF EXISTS {}".format(self.view_name))
        previous = self.pop_previous_sql(app_label)

        if previous:
            schema_editor.execute("CREATE VIEW {} AS {}".format(self.view_name, previous))

    def state_forwards(self, app_label, state):
        self.push_history(app_label)

    def describe(self):
        return "Create view {}".format(self.view_name)
