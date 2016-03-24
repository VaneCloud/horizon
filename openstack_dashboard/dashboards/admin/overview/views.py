# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

from django.conf import settings
from django.template.defaultfilters import floatformat  # noqa
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon.utils import csvbase

from openstack_dashboard import api
from openstack_dashboard import usage

from horizon import messages

from horizon import API


class GlobalUsageCsvRenderer(csvbase.BaseCsvResponse):

    if getattr(settings, 'METERING_ENABLED', False):
        columns = [_("Project Name"), _("VCPUs"), _("RAM (MB)"),
               _("Disk (GB)"), _("Usage (Hours)"), _("VCPU Costs"), _("Memory Costs"), _("Disk Costs")]
    else:
        columns = [_("Project Name"), _("VCPUs"), _("RAM (MB)"),
               _("Disk (GB)"), _("Usage (Hours)")]

    def get_row_data(self):
        if getattr(settings, 'METERING_ENABLED', False):
            for u in self.context['usage'].usage_list:
                yield (u.project_name or u.tenant_id,
                       u.vcpus,
                       u.memory_mb,
                       u.local_gb,
                       floatformat(u.vcpu_hours, 2),
                       floatformat(u.vcpu_costs, 2),
                       floatformat(u.memory_costs, 2),
                       floatformat(u.disk_costs,2))
        else:
            for u in self.context['usage'].usage_list:
                yield (u.project_name or u.tenant_id,
                       u.vcpus,
                       u.memory_mb,
                       u.local_gb,
                       floatformat(u.vcpu_hours, 2))


class GlobalOverview(usage.UsageView):
    table_class = usage.GlobalUsageTable
    usage_class = usage.GlobalUsage
    template_name = 'admin/overview/usage.html'
    csv_response_class = GlobalUsageCsvRenderer

    def get_context_data(self, **kwargs):
        context = super(GlobalOverview, self).get_context_data(**kwargs)
        context['monitoring'] = getattr(settings, 'EXTERNAL_MONITORING', [])

        request = self.request

        if getattr(settings, 'METERING_ENABLED', False):
            ifUpdatePrice = request.GET.get("update_price_name")

            prices = API.getPrice()

            vcpu_per_hour_price = prices[0]
            memory_per_hour_price = prices[1]
            disk_per_hour_price = prices[2]
            currency = prices[3]

            if ifUpdatePrice == 'update':
                vcpu_per_hour_price = request.GET.get("vcpu_per_hour_price")
                memory_per_hour_price = request.GET.get("memory_per_hour_price")
                disk_per_hour_price = request.GET.get("disk_per_hour_price")
                currency = request.GET.get("currencyName")
                isNum = True
                try:
                    float(vcpu_per_hour_price)
                    float(memory_per_hour_price)
                    float(disk_per_hour_price)
                except(ValueError):
                    isNum = False
                if isNum:
                    flag = API.updatePrice(vcpu_per_hour_price,memory_per_hour_price,disk_per_hour_price,currency)
                    if flag:
                        messages.success(request,_("Update successfully!"))
                    else:
                        vcpu_per_hour_price = prices[0]
                        memory_per_hour_price = prices[1]
                        disk_per_hour_price = prices[2]
                        currency = prices[3]
                        messages.error(request,_("Update failed!"))
                else:
                    vcpu_per_hour_price = prices[0]
                    memory_per_hour_price = prices[1]
                    disk_per_hour_price = prices[2]
                    currency = prices[3]
                    messages.error(request,_("Please input correct value!"))

            context['vcpu_per_hour_price'] = vcpu_per_hour_price
            context['memory_per_hour_price'] = memory_per_hour_price
            context['disk_per_hour_price'] = disk_per_hour_price
            context['currency'] = currency

        context['METERING_ENABLED'] = getattr(settings,
                                              'METERING_ENABLED',
                                               False)
        return context

    def get_data(self):
        data = super(GlobalOverview, self).get_data()
        # Pre-fill project names
        try:
            projects, has_more = api.keystone.tenant_list(self.request)
        except Exception:
            projects = []
            exceptions.handle(self.request,
                              _('Unable to retrieve project list.'))
        for instance in data:
            project = filter(lambda t: t.id == instance.tenant_id, projects)
            # If we could not get the project name, show the tenant_id with
            # a 'Deleted' identifier instead.
            if project:
                instance.project_name = getattr(project[0], "name", None)
            else:
                deleted = _("Deleted")
                instance.project_name = translation.string_concat(
                    instance.tenant_id, " (", deleted, ")")
        return data
