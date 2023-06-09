# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\directory_watcher_service.py
# Compiled at: 2016-10-31 18:09:01
# Size of source mod 2**32: 4795 bytes
from singletons import DEFAULT
import sims4.core_services, sims4.directory_watcher_handler, sims4.service_manager
if sims4.core_services.SUPPORT_RELOADING_SCRIPTS:
    __all__ = ['DirectoryWatcherService']

    class DirectoryWatcherService(sims4.service_manager.Service):

        class DirectoryWatcherChangeHandler(sims4.directory_watcher_handler.DirectoryWatcherHandler):

            def __init__(self):
                super().__init__()
                self._path_list = None

            def _paths(self):
                return self._path_list

            def set_paths(self, paths):
                self._path_list = paths

            def _handle(self, filename):
                sims4.core_services.directory_watcher_manager().register_change(filename)

        def __init__(self):
            self.directory_watcher_handler = self.DirectoryWatcherChangeHandler()
            self.change_sets = {}

        def set_paths(self, paths, set_name=None):
            was_running = self.directory_watcher_handler._watcher is not None
            self.directory_watcher_handler.stop()
            self.directory_watcher_handler.set_paths(paths)
            if set_name is not None:
                self.create_set(set_name, allow_existing=True)
            if was_running:
                if self.change_sets:
                    self.directory_watcher_handler.start()

        def stop(self):
            self.directory_watcher_handler.stop()

        def on_tick(self):
            self.directory_watcher_handler.on_tick()

        def create_set(self, name, allow_existing=False):
            if name in self.change_sets:
                if allow_existing:
                    return
                raise KeyError("A change set with the name '{}' already exists.".format(name))
            self.change_sets[name] = set()
            if self.change_sets:
                self.directory_watcher_handler.start()

        def register_change(self, filename, setname=None):
            if setname is not None:
                self.change_sets[setname].add(filename)
            else:
                for change_set in self.change_sets.values():
                    change_set.add(filename)

        def get_changes(self, name):
            return set(self.change_sets[name])

        def get_change_sets(self):
            return {name: set(change_set) for name, change_set in self.change_sets.items()}

        def consume_set(self, name):
            change_set = self.change_sets[name]
            self.change_sets[name] = set()
            return change_set

        def remove_set(self, name):
            del self.change_sets[name]
            if not self.change_sets:
                self.directory_watcher_handler.stop()