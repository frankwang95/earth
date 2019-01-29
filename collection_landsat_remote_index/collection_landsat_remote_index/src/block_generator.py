from lib_learning.collection.base_generator import WorkBlockGenerator


class LandSatRemoteIndexBlockGenerator(WorkBlockGenerator):
    def __init__(self, base_api, start_row=1, start_path=1, max_row=248, max_path=233):
        self.base_api = base_api
        self.max_row = max_row
        self.max_path = max_path
        self.row = start_row
        self.path = start_path


    def get_url(self, row, path):
        return "{}/search?row={}&path={}&full=true".format(self.base_api, row, path)


    def increment_row_path(self):
        self.row += 1
        if self.row > self.max_row:
            self.row = 1
            self.path = (self.path % self.max_path) + 1


    def get_next(self, row=None, path=None):
        if row is None:
            assert path is None
            output_row, output_path = self.row, self.path
            self.increment_row_path()
            return {'url': self.get_url(output_row, output_path)}

        assert isinstance(row, int) and isinstance(path, int)
        return {'url': self.get_url(row, path)}
