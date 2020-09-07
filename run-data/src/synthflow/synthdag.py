from airflow import DAG


class SynthNameContext:
    __name_context = []

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        SynthNameContext.__name_context.append(self.name)

    def __exit__(self, type, value, traceback):
        SynthNameContext.__name_context.pop()

    @classmethod
    def current(cls):
        if not SynthNameContext.__name_context:
            return None

        return SynthNameContext.__name_context[-1]


class SynthDAG(DAG):
    def __init__(self, dag_id, **kwargs):
        full_id = f'{dag_id}-{SynthNameContext.current()}'
        super(SynthDAG, self).__init__(full_id, **kwargs)