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


from django.template.defaultfilters import capfirst  # noqa
from django.template.defaultfilters import floatformat  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon.utils import csvbase
from horizon import views

from openstack_dashboard import usage
from django.conf import settings
from openstack_dashboard.usage import quotas

from horizon import API

from horizon import meteringConfig

class ProjectUsageCsvRenderer(csvbase.BaseCsvResponse):

    columns = [_("Instance Name"), _("VCPUs"), _("RAM (MB)"),
               _("Disk (GB)"), _("Usage (Hours)"),
               _("Uptime (Seconds)"), _("State")]

    def get_row_data(self):

        for inst in self.context['usage'].get_instances():
            yield (inst['name'],
                   inst['vcpus'],
                   inst['memory_mb'],
                   inst['local_gb'],
                   floatformat(inst['hours'], 2),
                   inst['uptime'],
                   capfirst(inst['state']))


class ProjectOverview(usage.UsageView):
    table_class = usage.ProjectUsageTable
    usage_class = usage.ProjectUsage
    template_name = 'project/overview/usage.html'
    csv_response_class = ProjectUsageCsvRenderer

    def get_data(self):
        super(ProjectOverview, self).get_data()
        return self.usage.get_instances()

    def _has_permission(self, policy):
        has_permission = True
        policy_check = getattr(settings, "POLICY_CHECK_FUNCTION", None)

        if policy_check:
            has_permission = policy_check(policy, self.request)

        return has_permission

    def _quota_exceeded(self, quota):
        usages = quotas.tenant_quota_usages(self.request)
        available = usages.get(quota, {}).get('available', 1)
        return available <= 0

    def get_context_data(self, **kwargs):
        context = super(ProjectOverview, self).get_context_data(**kwargs)

        context['meteringFeatureEnabled'] = meteringConfig.meteringFeatureEnabled

        if meteringConfig.meteringFeatureEnabled:
            vcpu_hours = self.usage.summary['vcpu_hours']
            memory_mb_hours = self.usage.summary['memory_mb_hours']
            disk_gb_hours = self.usage.summary['disk_gb_hours']

            prices = API.getPrice()
            vcpupricePer = prices[0]
            memorypricePer = prices[1]
            diskpricePer = prices[2]
            currency = prices[3]

            vcpuMoney = vcpu_hours * vcpupricePer
            memoryMoney = memory_mb_hours * memorypricePer
            diskMoney = disk_gb_hours * diskpricePer
            totalMoney = vcpuMoney + diskMoney + memoryMoney

            context['vcpuMoney'] = vcpuMoney
            context['memoryMoney'] = memoryMoney
            context['diskMoney'] = diskMoney
            context['totalMoney'] = totalMoney
            context['currency'] = currency
        network_config = getattr(settings, 'OPENSTACK_NEUTRON_NETWORK', {})

        context['launch_instance_allowed'] = self._has_permission(
            (("compute", "compute:create"),))
        context['instance_quota_exceeded'] = self._quota_exceeded('instances')
        context['create_network_allowed'] = self._has_permission(
            (("network", "create_network"),))
        context['network_quota_exceeded'] = self._quota_exceeded('networks')
        context['create_router_allowed'] = (
            network_config.get('enable_router', True) and
            self._has_permission((("network", "create_router"),)))
        context['router_quota_exceeded'] = self._quota_exceeded('routers')
        context['console_type'] = getattr(
            settings, 'CONSOLE_TYPE', 'AUTO')
        context['show_ng_launch'] = getattr(
            settings, 'LAUNCH_INSTANCE_NG_ENABLED', False)
        return context


class WarningView(views.HorizonTemplateView):
    template_name = "project/_warning.html"
