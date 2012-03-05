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
        klass = midware.db.get('rs_group:%s' % group)
        if klass:
            # We have our rate-limit group!
            environ['turnstile.nova.limitclass'] = klass
