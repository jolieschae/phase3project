# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\tracemalloc.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 17610 bytes
from collections.abc import Sequence, Iterable
from functools import total_ordering
import fnmatch, linecache, os.path, pickle
from _tracemalloc import *
from _tracemalloc import _get_object_traceback, _get_traces

def _format_size(size, sign):
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB'):
        if abs(size) < 100:
            if unit != 'B':
                if sign:
                    return '%+.1f %s' % (size, unit)
                return '%.1f %s' % (size, unit)
        if not abs(size) < 10240:
            if unit == 'TiB':
                if sign:
                    return '%+.0f %s' % (size, unit)
                return '%.0f %s' % (size, unit)
            size /= 1024


class Statistic:
    __slots__ = ('traceback', 'size', 'count')

    def __init__(self, traceback, size, count):
        self.traceback = traceback
        self.size = size
        self.count = count

    def __hash__(self):
        return hash((self.traceback, self.size, self.count))

    def __eq__(self, other):
        return self.traceback == other.traceback and self.size == other.size and self.count == other.count

    def __str__(self):
        text = '%s: size=%s, count=%i' % (
         self.traceback,
         _format_size(self.size, False),
         self.count)
        if self.count:
            average = self.size / self.count
            text += ', average=%s' % _format_size(average, False)
        return text

    def __repr__(self):
        return '<Statistic traceback=%r size=%i count=%i>' % (
         self.traceback, self.size, self.count)

    def _sort_key(self):
        return (
         self.size, self.count, self.traceback)


class StatisticDiff:
    __slots__ = ('traceback', 'size', 'size_diff', 'count', 'count_diff')

    def __init__(self, traceback, size, size_diff, count, count_diff):
        self.traceback = traceback
        self.size = size
        self.size_diff = size_diff
        self.count = count
        self.count_diff = count_diff

    def __hash__(self):
        return hash((self.traceback, self.size, self.size_diff,
         self.count, self.count_diff))

    def __eq__(self, other):
        return self.traceback == other.traceback and self.size == other.size and self.size_diff == other.size_diff and self.count == other.count and self.count_diff == other.count_diff

    def __str__(self):
        text = '%s: size=%s (%s), count=%i (%+i)' % (
         self.traceback,
         _format_size(self.size, False),
         _format_size(self.size_diff, True),
         self.count,
         self.count_diff)
        if self.count:
            average = self.size / self.count
            text += ', average=%s' % _format_size(average, False)
        return text

    def __repr__(self):
        return '<StatisticDiff traceback=%r size=%i (%+i) count=%i (%+i)>' % (
         self.traceback, self.size, self.size_diff,
         self.count, self.count_diff)

    def _sort_key(self):
        return (
         abs(self.size_diff), self.size,
         abs(self.count_diff), self.count,
         self.traceback)


def _compare_grouped_stats(old_group, new_group):
    statistics = []
    for traceback, stat in new_group.items():
        previous = old_group.pop(traceback, None)
        if previous is not None:
            stat = StatisticDiff(traceback, stat.size, stat.size - previous.size, stat.count, stat.count - previous.count)
        else:
            stat = StatisticDiff(traceback, stat.size, stat.size, stat.count, stat.count)
        statistics.append(stat)

    for traceback, stat in old_group.items():
        stat = StatisticDiff(traceback, 0, -stat.size, 0, -stat.count)
        statistics.append(stat)

    return statistics


@total_ordering
class Frame:
    __slots__ = ('_frame', )

    def __init__(self, frame):
        self._frame = frame

    @property
    def filename(self):
        return self._frame[0]

    @property
    def lineno(self):
        return self._frame[1]

    def __eq__(self, other):
        return self._frame == other._frame

    def __lt__(self, other):
        return self._frame < other._frame

    def __hash__(self):
        return hash(self._frame)

    def __str__(self):
        return '%s:%s' % (self.filename, self.lineno)

    def __repr__(self):
        return '<Frame filename=%r lineno=%r>' % (self.filename, self.lineno)


@total_ordering
class Traceback(Sequence):
    __slots__ = ('_frames', )

    def __init__(self, frames):
        Sequence.__init__(self)
        self._frames = tuple(reversed(frames))

    def __len__(self):
        return len(self._frames)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple((Frame(trace) for trace in self._frames[index]))
        return Frame(self._frames[index])

    def __contains__(self, frame):
        return frame._frame in self._frames

    def __hash__(self):
        return hash(self._frames)

    def __eq__(self, other):
        return self._frames == other._frames

    def __lt__(self, other):
        return self._frames < other._frames

    def __str__(self):
        return str(self[0])

    def __repr__(self):
        return '<Traceback %r>' % (tuple(self),)

    def format(self, limit=None, most_recent_first=False):
        lines = []
        if limit is not None:
            if limit > 0:
                frame_slice = self[-limit:]
            else:
                frame_slice = self[:limit]
        else:
            frame_slice = self
        if most_recent_first:
            frame_slice = reversed(frame_slice)
        for frame in frame_slice:
            lines.append('  File "%s", line %s' % (
             frame.filename, frame.lineno))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                lines.append('    %s' % line)

        return lines


def get_object_traceback(obj):
    frames = _get_object_traceback(obj)
    if frames is not None:
        return Traceback(frames)
    return


class Trace:
    __slots__ = ('_trace', )

    def __init__(self, trace):
        self._trace = trace

    @property
    def domain(self):
        return self._trace[0]

    @property
    def size(self):
        return self._trace[1]

    @property
    def traceback(self):
        return Traceback(self._trace[2])

    def __eq__(self, other):
        return self._trace == other._trace

    def __hash__(self):
        return hash(self._trace)

    def __str__(self):
        return '%s: %s' % (self.traceback, _format_size(self.size, False))

    def __repr__(self):
        return '<Trace domain=%s size=%s, traceback=%r>' % (
         self.domain, _format_size(self.size, False), self.traceback)


class _Traces(Sequence):

    def __init__(self, traces):
        Sequence.__init__(self)
        self._traces = traces

    def __len__(self):
        return len(self._traces)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return tuple((Trace(trace) for trace in self._traces[index]))
        return Trace(self._traces[index])

    def __contains__(self, trace):
        return trace._trace in self._traces

    def __eq__(self, other):
        return self._traces == other._traces

    def __repr__(self):
        return '<Traces len=%s>' % len(self)


def _normalize_filename(filename):
    filename = os.path.normcase(filename)
    if filename.endswith('.pyc'):
        filename = filename[:-1]
    return filename


class BaseFilter:

    def __init__(self, inclusive):
        self.inclusive = inclusive

    def _match(self, trace):
        raise NotImplementedError


class Filter(BaseFilter):

    def __init__(self, inclusive, filename_pattern, lineno=None, all_frames=False, domain=None):
        super().__init__(inclusive)
        self.inclusive = inclusive
        self._filename_pattern = _normalize_filename(filename_pattern)
        self.lineno = lineno
        self.all_frames = all_frames
        self.domain = domain

    @property
    def filename_pattern(self):
        return self._filename_pattern

    def _match_frame_impl(self, filename, lineno):
        filename = _normalize_filename(filename)
        if not fnmatch.fnmatch(filename, self._filename_pattern):
            return False
        if self.lineno is None:
            return True
        return lineno == self.lineno

    def _match_frame(self, filename, lineno):
        return self._match_frame_impl(filename, lineno) ^ (not self.inclusive)

    def _match_traceback(self, traceback):
        if self.all_frames:
            if any((self._match_frame_impl(filename, lineno) for filename, lineno in traceback)):
                return self.inclusive
            return not self.inclusive
        else:
            filename, lineno = traceback[0]
            return self._match_frame(filename, lineno)

    def _match(self, trace):
        domain, size, traceback = trace
        res = self._match_traceback(traceback)
        if self.domain is not None:
            if self.inclusive:
                return res and domain == self.domain
            return res or domain != self.domain
        return res


class DomainFilter(BaseFilter):

    def __init__(self, inclusive, domain):
        super().__init__(inclusive)
        self._domain = domain

    @property
    def domain(self):
        return self._domain

    def _match(self, trace):
        domain, size, traceback = trace
        return (domain == self.domain) ^ (not self.inclusive)


class Snapshot:

    def __init__(self, traces, traceback_limit):
        self.traces = _Traces(traces)
        self.traceback_limit = traceback_limit

    def dump(self, filename):
        with open(filename, 'wb') as (fp):
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as (fp):
            return pickle.load(fp)

    def _filter_trace(self, include_filters, exclude_filters, trace):
        if include_filters:
            if not any((trace_filter._match(trace) for trace_filter in include_filters)):
                return False
        if exclude_filters:
            if any((not trace_filter._match(trace) for trace_filter in exclude_filters)):
                return False
        return True

    def filter_traces(self, filters):
        if not isinstance(filters, Iterable):
            raise TypeError('filters must be a list of filters, not %s' % type(filters).__name__)
        elif filters:
            include_filters = []
            exclude_filters = []
            for trace_filter in filters:
                if trace_filter.inclusive:
                    include_filters.append(trace_filter)
                else:
                    exclude_filters.append(trace_filter)

            new_traces = [trace for trace in self.traces._traces if self._filter_trace(include_filters, exclude_filters, trace)]
        else:
            new_traces = self.traces._traces.copy()
        return Snapshot(new_traces, self.traceback_limit)

    def _group_by(self, key_type, cumulative):
        if key_type not in ('traceback', 'filename', 'lineno'):
            raise ValueError('unknown key_type: %r' % (key_type,))
        else:
            if cumulative:
                if key_type not in ('lineno', 'filename'):
                    raise ValueError('cumulative mode cannot by used with key type %r' % key_type)
            stats = {}
            tracebacks = {}
            if not cumulative:
                for trace in self.traces._traces:
                    domain, size, trace_traceback = trace
                    try:
                        traceback = tracebacks[trace_traceback]
                    except KeyError:
                        if key_type == 'traceback':
                            frames = trace_traceback
                        else:
                            if key_type == 'lineno':
                                frames = trace_traceback[:1]
                            else:
                                frames = (
                                 (
                                  trace_traceback[0][0], 0),)
                        traceback = Traceback(frames)
                        tracebacks[trace_traceback] = traceback

                    try:
                        stat = stats[traceback]
                        stat.size += size
                        stat.count += 1
                    except KeyError:
                        stats[traceback] = Statistic(traceback, size, 1)

            else:
                for trace in self.traces._traces:
                    domain, size, trace_traceback = trace
                    for frame in trace_traceback:
                        try:
                            traceback = tracebacks[frame]
                        except KeyError:
                            if key_type == 'lineno':
                                frames = (
                                 frame,)
                            else:
                                frames = (
                                 (
                                  frame[0], 0),)
                            traceback = Traceback(frames)
                            tracebacks[frame] = traceback

                        try:
                            stat = stats[traceback]
                            stat.size += size
                            stat.count += 1
                        except KeyError:
                            stats[traceback] = Statistic(traceback, size, 1)

        return stats

    def statistics(self, key_type, cumulative=False):
        grouped = self._group_by(key_type, cumulative)
        statistics = list(grouped.values())
        statistics.sort(reverse=True, key=(Statistic._sort_key))
        return statistics

    def compare_to(self, old_snapshot, key_type, cumulative=False):
        new_group = self._group_by(key_type, cumulative)
        old_group = old_snapshot._group_by(key_type, cumulative)
        statistics = _compare_grouped_stats(old_group, new_group)
        statistics.sort(reverse=True, key=(StatisticDiff._sort_key))
        return statistics


def take_snapshot():
    if not is_tracing():
        raise RuntimeError('the tracemalloc module must be tracing memory allocations to take a snapshot')
    traces = _get_traces()
    traceback_limit = get_traceback_limit()
    return Snapshot(traces, traceback_limit)