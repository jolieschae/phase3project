# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\venue_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 7045 bytes
import collections, sims4.commands
from server_commands.argument_helpers import TunableInstanceParam
from venues.venue_service import VenueService
import build_buy, services

@sims4.commands.Command('venues.set_venue')
def set_venue(venue_tuning: TunableInstanceParam(sims4.resources.Types.VENUE), _connection=None):
    if venue_tuning is None:
        sims4.commands.output('Requesting an unknown venue type: {0}'.format(venue_tuning), _connection)
        return False
    venue_game_service = services.venue_game_service()
    if venue_game_service is None:
        return services.venue_service().on_change_venue_type_at_runtime(venue_tuning)
    return venue_game_service.change_venue_type(services.current_zone_id(), venue_tuning)


@sims4.commands.Command('venues.get_venue')
def get_venue(_connection=None):
    venue_service = services.venue_service()
    if venue_service is None:
        sims4.commands.output('None, None', _connection)
        return
    sims4.commands.output('{}, {}'.format(type(venue_service.source_venue).__name__, type(venue_service.active_venue).__name__), _connection)


@sims4.commands.Command('venues.test_all_venues')
def test_all_venues(_connection=None):
    venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
    active_lot = services.active_lot()
    for venue_tuning in venue_manager.types.values:
        result, result_message = venue_tuning.lot_has_required_venue_objects(active_lot)
        venue_name = venue_tuning.__name__
        if result:
            sims4.commands.output('{0}: Active lot can become venue'.format(venue_name), _connection)
        else:
            sims4.commands.output('{0}: Active lot cannot become venue.\nFailure Reasons: {1}'.format(venue_name, result_message), _connection)

    return True


PrintVenueLog = collections.namedtuple('PrintVenueLog', [
 "'Neighborhood_Name'", 
 "'Neighborhood_ID'", 
 "'Lot_Description_ID'", 
 "'Zone_Instance_ID'", 
 "'Venue_Tuning_Name'", 
 "'Lot_Name'"])

@sims4.commands.Command('venues.print_venues')
def print_venues(_connection=None):
    current_zone = services.current_zone()
    lot = current_zone.lot
    neighborhood_id = current_zone.neighborhood_id
    world_description_id = services.get_world_description_id(current_zone.world_id)
    lot_description_id = services.get_lot_description_id(lot.lot_id, world_description_id)
    neighborhood_description_id = services.get_persistence_service().get_neighborhood_proto_buff(neighborhood_id).region_id

    def print_line():
        sims4.commands.output('------------------------------------------------------------------------------------------------------------------------------------------------------', _connection)

    print_line()
    sims4.commands.output('Current Game Stats: \nLot Id: {}\nLot Description Id: {}\nWorld/Street Description Id: {}\nRegion/Neighborhood Description Id: {}'.format(lot.lot_id, lot_description_id, world_description_id, neighborhood_description_id), _connection)
    print_line()
    venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
    venues = []
    for neighborhood_proto in services.get_persistence_service().get_neighborhoods_proto_buf_gen():
        for lot_owner_info in neighborhood_proto.lots:
            zone_id = lot_owner_info.zone_instance_id
            if zone_id is not None:
                venue_tuning_id = build_buy.get_current_venue(zone_id)
                venue_tuning = venue_manager.get(venue_tuning_id)
                if venue_tuning is not None:
                    log = PrintVenueLog._make((neighborhood_proto.name,
                     neighborhood_proto.region_id,
                     lot_owner_info.lot_description_id,
                     zone_id,
                     venue_tuning.__name__,
                     lot_owner_info.lot_name))
                    venues.append(log)

    str_format = '{:20} ({:{center}15}) {:{center}20} {:15} ({:{center}20}) {:20}'

    def print_columns():
        sims4.commands.output(str_format.format('Neighborhood_Name', 'Neighborhood_ID', 'Lot_Description_ID', 'Zone_Instance_ID',
          'Venue_Tuning_Name', 'Lot_Name', center='^'), _connection)

    print_columns()
    print_line()
    for venue in sorted(venues):
        sims4.commands.output(str_format.format((venue.Neighborhood_Name), (venue.Neighborhood_ID),
          (venue.Lot_Description_ID),
          (venue.Zone_Instance_ID),
          (venue.Venue_Tuning_Name),
          (venue.Lot_Name),
          center='^'), _connection)

    print_line()
    print_columns()


@sims4.commands.Command('venues.change_zone_director')
def change_zone_director(zone_director_tuning: TunableInstanceParam(sims4.resources.Types.ZONE_DIRECTOR), run_cleanup: bool=True, _connection=None):
    output = sims4.commands.Output(_connection)
    if zone_director_tuning is None:
        output('Unknown zone director type')
        return False
    new_zone_director = zone_director_tuning()
    services.venue_service().change_zone_director(new_zone_director, run_cleanup)
    return True


@sims4.commands.Command('venues.print_zone_director')
def print_zone_director(_connection=None):
    output = sims4.commands.Output(_connection)
    zone_director = services.venue_service().get_zone_director()
    output('Zone Director: ' + str(zone_director))
    return True


@sims4.commands.Command('venues.clean_lot')
def clean_lot(connection=None):
    cleanup = VenueService.VENUE_CLEANUP_ACTIONS()
    cleanup.modify_objects()
    return True