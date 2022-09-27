#!/usr/bin/env python3

import logging
import sys
import argparse
import requests
import json

import gi
gi.require_version( 'Secret', '1' )
from gi.repository import Secret

def get_ha_password( ha_host : str, ha_port : int, user: str ) -> str:

    ''' Get the bearer token from Secret Service or store new one if none
    present. '''

    logger = logging.getLogger( 'get.password' )

    ha_schema = Secret.Schema.new(
        'info.interfinitydynamics.hatool',
        Secret.SchemaFlags.NONE,
        {
            'ha_host': Secret.SchemaAttributeType.STRING,
            'ha_port': Secret.SchemaAttributeType.INTEGER,
            'ha_user': Secret.SchemaAttributeType.STRING
        }
    )

    attributes = {
        'ha_host': ha_host,
        'ha_port': str( ha_port ),
        'ha_user': 'bearer'
    }

    label = '{}:{}:{}'.format( ha_host, ha_port, 'bearer' )
    logger.debug( 'looking up password for %s...', label )

    password = Secret.password_lookup_sync( ha_schema, attributes, None )
    if not password:
        # TODO: Ask for password.
        #Secret.password_store_sync( ha_schema, attributes,
        #    Secret.COLLECTION_DEFAULT, label, '', None )
        sys.exit( 0 )

    #logger.debug( 'password: %s', password )

    return password

def ha_api_request(
    host : str, port : str, bearer : str, entity : str, data : dict
) -> dict:

    ''' Query the Home Assistant API. Perform POST if data is provided or GET
    if not. '''

    logger = logging.getLogger( 'ha.request' )

    # Send API request.
    url = "https://{}:{}/api/states/{}".format( host, port, entity )
    if data:
        data_json = json.dumps( data )
        logger.debug( 'sending state %s to %s...', data_json, url )
        headers = {
            "Authorization": "Bearer {}".format( bearer ),
            "content-type": "application/json",
        }
        response = requests.post( url, headers=headers, data=data_json )
    else:
        # Just poll for status.
        logger.debug( 'getting state from %s...', url )
        headers = {
            "Authorization": "Bearer {}".format( bearer ),
            "content-type": "application/json",
        }
        response = requests.get( url, headers=headers )

    response.raise_for_status()

    return response.json()

def main():

    parser = argparse.ArgumentParser(
        description='Simple Home Assistant API tool.' )

    parser.add_argument( '-v', '--verbose', action='store_true',
        help='Show debug log.' )

    parser.add_argument( '-c', '--config', default='power1.json',
        help='Path to config file with hostname/port.' )

    parser.add_argument( '-s', '--state',
        help='State to send to entity. (e.g. "on", "off")' )

    parser.add_argument( '-e', '--entity', required=True,
        help='Entity to get/set state on.' )

    args = parser.parse_args()

    # Setup logging.
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig( level=log_level )
    logger = logging.getLogger( 'main' )

    # Open config file.
    logger.debug( 'opening config file %s...', args.config )
    config = None
    with open( args.config, 'r' ) as config_file:
        config = json.loads( config_file.read() )

    # 'bearer' is a placeholder and not an actual username.
    password = get_ha_password( config['host'], config['port'], 'bearer' )

    data = None
    response = None
    if args.state:
        data = { 'state': args.state }
    try:
        response = ha_api_request(
            config['host'], config['port'], password, args.entity, data )
    except Exception as e:
        logger.error( 'error accessing HA: %s', e )

    if response:
        logger.info( response )

if '__main__' == __name__:
    main()

