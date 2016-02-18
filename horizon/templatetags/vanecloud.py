# Copyright 2012 Nebula, Inc.
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

from __future__ import absolute_import


from django import template

from horizon.base import Horizon  # noqa


register = template.Library()


@register.filter
def next_setp_id(steps, index):
    try:
        return steps[index].get_id()
    except:
        return None


@register.filter
def pre_setp_id(steps, index):
    try:
        print index
        return steps[index-2].get_id()
    except:
        return None
