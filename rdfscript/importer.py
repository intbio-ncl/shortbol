import pathlib

class Importer:

    def __init__(self, paths):

        self._dirs = [pathlib.Path(path).expanduser().resolve() for path in paths]
        self._dirs.append(pathlib.Path('.').resolve())

    @property
    def path(self):
        return self._dirs

    @property
    def extension(self):
        return '.shb'

    def add_path(self, newpath):
        self._dirs.append(self.to_absolute(pathlib.Path(newpath)))

    def remove_path(self, path):
        self._dirs.remove(self.to_absolute(pathlib.Path(path)))

    def import_file(self, filepath):

        for d in self._dirs:
            try:
                path = (d / filepath).with_suffix('.shb')
                data = path.read_text()
                self.add_path(path.parent)
                return data
            except FileNotFoundError:
                pass

        return self.try_absolute(filepath)

    def to_absolute(self, pathlib_path):
        return pathlib_path.expanduser().resolve()

    def try_absolute(self, filepath):

        try:
            absolute = self.to_absolute(pathlib.Path(filepath))
            path = absolute.with_suffix(self.extension)
            data = path.read_text()
            self.add_path(path.parent)
            return data
        except FileNotFoundError:
            return None
