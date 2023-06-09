# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\perf_test_commands.py
# Compiled at: 2020-11-16 14:58:03
# Size of source mod 2**32: 11632 bytes
import server_commands, services, sims4.commands, profile_utils, sims4.geometry, math, timeit, performance.test_profiling_setup
from sims4.math import Vector2
try:
    import _profile
    manitude_test_function = _profile.manitude_test_function
    no_op_function = _profile.no_op_function
except ImportError:

    def manitude_test_function(*_, **__):
        pass


    def no_op_function(*_, **__):
        pass


@sims4.commands.Command('profile_util.clear_profile_utils')
def clear_profile_utils():
    for function in profile_utils.all_profile_functions:
        function.num_calls = 0
        function.total_time = 0


@sims4.commands.Command('profile_util.main_profile')
@profile_utils.profile_function(show_enter=True, output_filename='main_profile')
def main_profile(num_loops: int=1000):
    no_op_test(num_loops)
    math_tests(num_loops)
    list_comp_test(num_loops)
    string_manipulation_tests(num_loops)
    dictionary_tests(num_loops)
    bool_conversion_test()


@sims4.commands.Command('profile_util.posture_graph_profile')
@profile_utils.profile_function(show_enter=True, output_filename='posture_graph_profile')
def posture_graph_profile(num_loops: int=1000):
    posture_graph_test(num_loops)


@sims4.commands.Command('profile_util.test_caches_profile')
def test_caches_profile(number_of_runs: int=500, clear_ratio: int=10):
    performance.test_profiling_setup.TestProfilingSetup.start_tests(number_of_runs, clear_ratio)


def nothing_func():
    pass


def string_manipulation_tests(num_loops):
    profile_utils.add_string('----- String Concat Test -----')
    putting = 'Putting'
    strings = 'Strings'
    together = 'Together'
    is_var = 'is'
    fun = 'Fun'
    profile_utils.sub_time_start()
    string = ''
    for index in range(num_loops):
        string += putting + ' ' + strings + ' ' + together + ' ' + is_var + ' ' + fun

    profile_utils.sub_time_end('Python: += Putting + Strings + Together + Is + Fun')
    profile_utils.sub_time_start()
    string6 = ''
    for index in range(num_loops):
        string6.join((string6, putting.join((' ', strings, ' ', together, ' ', is_var, ' ', fun))))

    profile_utils.sub_time_end('Python: str.join(str, Putting.join(Strings, Together, Is, Fun))')
    profile_utils.sub_time_start()
    string2 = ''
    for index in range(num_loops):
        string2.join((string2, '{} {} {} {} {}'.format(putting, strings, together, is_var, fun)))

    profile_utils.sub_time_end('Python: str.join(str, .format(Putting, Strings, Together, Is, Fun))')
    profile_utils.sub_time_start()
    for index in range(num_loops):
        string3 = 'CurIndex: ' + str(index)

    profile_utils.sub_time_end('Python: str = CurIndex: + index')
    profile_utils.sub_time_start()
    for index in range(num_loops):
        string4 = 'CurIndex: {}'.format(index)

    profile_utils.sub_time_end('Python: = CurIndex.format(index)')


def no_op_test(num_loops):
    profile_utils.add_string('----- No Op Test -----')
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        nothing_func()

    profile_utils.sub_time_end('Python: {} no_op calls'.format(num_loops))
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        no_op_function()

    profile_utils.sub_time_end('C++   : {} no_op calls'.format(num_loops))


def math_tests(num_loops):
    profile_utils.add_string('----- Various Magnitude Calculation Tests -----')
    profile_utils.sub_time_start()
    value = 0
    for index in range(num_loops):
        value += math.sqrt(index * index + (index + 1 * index + 1))

    profile_utils.sub_time_end('Python: {} 2d vector magnitude calcs, Val: {}'.format(num_loops, value))
    profile_utils.sub_time_start()
    value = full_magnitude(num_loops)
    profile_utils.sub_time_end('Python: {} 2d vector magnitude calcs, all inside python function, Val: {}'.format(num_loops, value))
    profile_utils.sub_time_start()
    value = 0
    for index in range(num_loops):
        value += magnitude(index)

    profile_utils.sub_time_end('Python: {} 2d vector magnitude calcs, PyLoop calls magnitude func, Val: {}'.format(num_loops, value))
    profile_utils.sub_time_start()
    value = manitude_test_function(num_loops)
    profile_utils.sub_time_end('C++   : {} 2d vector magnitude calcs, Loop in C++, Val: {}'.format(num_loops, value))


def full_magnitude(num_loops):
    value = 0
    for index in range(num_loops):
        value += math.sqrt(index * index + (index + 1 * index + 1))

    return value


def magnitude(num):
    return math.sqrt(num * num + (num + 1 * num + 1))


def dictionary_tests(num_loops):
    profile_utils.add_string('----- Dictionary Test -----')
    the_dict = {}
    string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for char in string:
        the_dict[char] = 5

    the_dict['this_item'] = 15
    for char in string:
        the_dict[char + char] = 10

    temp_var = 0
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        if 'this_item' in the_dict:
            temp_var = the_dict['this_item']

    profile_utils.sub_time_end('Python: if "this_item" in the_dict, then lookup (hits)')
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        try:
            temp_var = the_dict['this_item']
        except KeyError:
            pass

    profile_utils.sub_time_end('Python: try: temp_var = the_dict["this_item"] (hits)')
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        temp_var = the_dict.get('this_item', None)

    profile_utils.sub_time_end('Python: the_dict.get("this_item", None) (hits)')
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        if 'this_item_not_here' in the_dict:
            temp_var = the_dict['this_item_not_here']
        else:
            temp_var = None

    profile_utils.sub_time_end('Python: if "this_item_not_here" in the_dict:, then lookup (miss)')
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        try:
            temp_var = the_dict['this_item_not_here']
        except KeyError:
            temp_var = None

    profile_utils.sub_time_end('Python: try: temp_var = the_dict["this_item_not_here"] (miss)')
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        temp_var = the_dict.get('this_item_not_here', None)

    profile_utils.sub_time_end('Python: the_dict.get("this_item_not_here", None) (miss)')
    return temp_var


def list_comp_test(num_loops):
    profile_utils.add_string('----- List Comprehension Test -----')
    r0 = sims4.geometry.QtRect(Vector2(0, 0), Vector2(1, 1))
    r1 = sims4.geometry.QtRect(Vector2(0, 0), Vector2(2, 2))
    rect_list = []
    for _ in range(500):
        rect_list.append(r0)
        rect_list.append(r1)

    profile_utils.sub_time_start()
    new_list = []
    for rect in rect_list:
        new_list.append(rect.a)

    profile_utils.sub_time_end('Python: {} list appends & C++ accessor'.format(num_loops))
    profile_utils.sub_time_start()
    new_list2 = [rect.a for rect in rect_list]
    profile_utils.sub_time_end('Python: {} list appends & C++ accessor : list comprehension'.format(num_loops))


def bool_conversion_test(num_loops=1000000):
    profile_utils.add_string('----- Boolean Conversion Test -----')
    EXPRESSIONS = [
     "'l = None'", 
     "'l = False'", 
     "'l = 0'", 
     "'l = True'", 
     "'l = 1'", 
     '"l = \'\'"', 
     '"l = \'abc\'"', 
     "'l = ()'", 
     '"l = (\'a\', \'b\', \'c\')"', 
     "'l = []'", 
     "'l = list(range(10))'", 
     "'l = list(range(100))'", 
     "'l = list(range(1000))'", 
     "'l = {}'", 
     "'l = dict(zip(range(0, 100), (100, 200)))'"]
    APPROACHES = [
     "'bool(l)'", 
     "'len(l) > 0'", 
     "'not not l'", 
     "'True if l else False'", 
     "'if l:\\n    True\\nelse:\\n    False'"]
    for a in APPROACHES:
        profile_utils.add_string(">>> # Using '{1}'", 1, a.replace('\n', '\\n'))
        results = []
        for e in EXPRESSIONS:
            profile_utils.add_string(">>> timeit.timeit('{1}', '{2}', number={3})", 1, a.replace('\n', '\\n'), e, num_loops)
            try:
                t = timeit.timeit(a, e, number=num_loops)
                profile_utils.add_string('{1:.4}', 1, t)
                results.append(t)
            except:
                profile_utils.add_string('invalid', 1)

        if results:
            profile_utils.add_string('>>> # Average: {1:.4}\n', 1, sum(results) / len(results))


def posture_graph_test(num_loops: int):
    profile_utils.add_string('----- Posture Graph Test -----')
    num_loops = int(num_loops)
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        services.current_zone().posture_graph_service.rebuild()

    profile_utils.sub_time_end('Python: {} posture graph rebuild'.format(num_loops))
    sim = services.get_active_sim()
    queue = sim.queue
    timeline = services.time_service().sim_timeline
    pos = (200.0, 0.0, 188.0)
    connection = services.client_manager().get_first_client().id
    queue.cancel_all()
    server_commands.sim_commands.gohere((pos[0]), (pos[1]), (pos[2]), _connection=connection)
    interaction = queue.peek_head()
    if not interaction:
        profile_utils.add_string('Error: go here failed to queue up. Make sure you are running in the empty test lot.')
        return
    transition = interaction.transition
    num_loops *= 1000
    profile_utils.sub_time_start()
    for _ in range(num_loops):
        for transition in transition._get_transitions_for_sim(timeline, sim):
            pass

    profile_utils.sub_time_end('Python: {} get_transitions_for_sim'.format(num_loops))
    queue.cancel_all()