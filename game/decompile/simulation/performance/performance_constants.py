# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\performance\performance_constants.py
# Compiled at: 2020-04-23 22:29:54
# Size of source mod 2**32: 2178 bytes
NUM_SIMS = 'num_sims'
OBJS_ACTIVE_LOT_INTERACTIVE = '#Objects (Active Lot) Interactive'
OBJS_ACTIVE_LOT_DECORATIVE = '#Objects (Active Lot) Decorative'
OBJS_OPEN_STREET_INTERACTIVE = '#Objects (Open Streets) Interactive'
OBJS_OPEN_STREET_DECORATIVE = '#Objects (Open Streets) Decorative'
OBJS_ACTIVE_LOT_AUTONOMOUS_AFFORDANCE = '#Objects (Active Lot) Autonomous Affordances'
OBJS_OPEN_STREET_AUTONOMOUS_AFFORDANCE = '#Objects (Open Street) Autonomous Affordances'
OBJS_AUTONOMOUS_AFFORDANCE = '#Total Autonomous Affordances'
OBJS_INTERACTIVE = 'Objects(Interactive)'
OBJS_DECORATIVE = 'Objects(Decorative)'
OBJS_AUTONOMOUS = 'Objects(Autonomous)'
OBJS_TOTAL = 'Total Objects'
PROPS_TOTAL = 'Total Props'
OBJS_INVENTORY_TOTAL = 'Total Inventory Objects'
OBJS_GRAND_TOTAL = 'Grand Total (Objs,Props,InventoryObjs)'
TICKS_PER_SECOND = 'ticks_per_sec'
POSTURE_GRAPH_NODES = '#Posture Graph Nodes'
POSTURE_GRAPH_EDGES = '#Posture Graph Edges'
COUNT_PROPS = 'num_props'
COUNT_OBJECTS_PROPS = 'total_objects_props'
INTERACTIONS_AUTONOMOUS = 'Interactions(Autonomous)'
INTERACTIONS_USER_DIRECTED = 'Interactions(UserDirected)'
FIELD_NAME = 'name'
FIELD_LOCATION = 'location'
FIELD_FREQUENCY = 'frequency'
LOCATION_ACTIVE_LOT = 'active_lot'
LOCATION_OPEN_STREET = 'open_street'
OBJECT_CLASSIFICATIONS = [
 'OBJS_INTERACTIVE', 
 'OBJS_DECORATIVE', 
 'OBJS_AUTONOMOUS', 
 'INTERACTIONS_AUTONOMOUS', 
 'INTERACTIONS_USER_DIRECTED']
BUDGETS = {NUM_SIMS: 20, 
 OBJS_ACTIVE_LOT_INTERACTIVE: 350, 
 OBJS_ACTIVE_LOT_DECORATIVE: 250, 
 OBJS_OPEN_STREET_INTERACTIVE: 50, 
 OBJS_OPEN_STREET_DECORATIVE: 250, 
 OBJS_ACTIVE_LOT_AUTONOMOUS_AFFORDANCE: 250, 
 OBJS_TOTAL: 900, 
 POSTURE_GRAPH_NODES: 3000, 
 POSTURE_GRAPH_EDGES: 12000}