# Copyright 2012 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
from turnstile import tools


def rs_preprocess(midware, environ):
    """
    Pre-process requests to nova.  Derives the rate-limit class from
    the X-PP-Groups header.
    """

    # If we don't have the header, let nova_preprocess() do its magic.
    groups = environ.get('HTTP_X_PP_GROUPS')
    if not groups:
        return

    # Split the groups string into a list of groups
    # XXX Note: assuming space-separated here
    groups = groups.split()

    # Look up the rate-limit class from the database
    for group in groups:
        klass = midware.db.get('rs-group:%s' % group)
        if klass:
            # We have our rate-limit group!
            environ['turnstile.nova.limitclass'] = klass


def _group_class(config, group, klass=None, delete=False):
    """
    Set up or query limit classes associated with groups.

    :param config: Name of the configuration file, for connecting to
                   the Redis database.
    :param group: The name of the group.
    :param klass: If provided, the name of the class to map the group
                  to.
    :param delete: If True, deletes the group from the database.

    Returns the class associated with the given group.  Note that only
    one of `klass` or `delete` may be given.
    """

    # Connect to the database...
    db, _limits_key, _control_channel = tools.parse_config(config)

    # Get the key for the limit class...
    key = 'rs-group:%s' % group

    # Now, look up the tenant's current class
    old_klass = midware.db.get(key)

    # Do we need to delete it?  Change it?
    if delete:
        db.delete(key)
    elif klass and klass != old_klass:
        db.set(key, klass)

    return old_klass


def group_class():
    """
    Console script entry point for setting limit classes associated
    with particular groups.
    """

    parser = argparse.ArgumentParser(
        description="Set up or query limit classes associated with groups.",
        )

    parser.add_argument('config',
                        help="Name of the configuration file, for connecting "
                        "to the Redis database.")
    parser.add_argument('group',
                        help="Name of the group.")
    parser.add_argument('--debug', '-d',
                        dest='debug',
                        action='store_true',
                        default=False,
                        help="Run the tool in debug mode.")
    parser.add_argument('--delete', '-D',
                        dest='delete',
                        action='store_true',
                        default=False,
                        help="Delete the group from the database.")
    parser.add_argument('--class', '-c',
                        dest='klass',
                        action='store',
                        default=None,
                        help="If specified, sets the class associated with "
                        "the given group.")

    args = parser.parse_args()
    try:
        klass = _group_class(args.config, args.group, args.klass, args.delete)

        print "Group %s:" % args.group
        if args.klass or args.delete:
            if klass:
                print "  Previous rate-limit class: %s" % klass
            if args.delete:
                print "  Deleted from database"
            else:
                print "  New rate-limit class: %s" % args.klass
        elif klass:
            print "  Configured rate-limit class: %s" % klass
        else:
            print "  Not currently configured in database."
    except Exception as exc:
        if args.debug:
            raise
        return str(exc)
