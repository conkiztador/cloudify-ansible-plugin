# Copyright (c) 2019 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError, OperationRetry

from cloudify_ansible_sdk import (
    AnsiblePlaybookFromFile,
    CloudifyAnsibleSDKError,
    sources
)

from cloudify_ansible import (
    constants,
    ansible_playbook_node,
    ansible_relationship_source,
    utils
)


UNREACHABLE_CODES = [None, 2, 4]
SUCCESS_CODES = [0]


@operation
@ansible_playbook_node
def run(playbook_args, ansible_env_vars, _ctx, **_):

    _ctx.logger.debug('playbook_args: {0}'.format(playbook_args))

    try:
        playbook = AnsiblePlaybookFromFile(**playbook_args)
        utils.assign_environ(ansible_env_vars)
        output, error, return_code = playbook.execute()
    except CloudifyAnsibleSDKError:
        raise NonRecoverableError(CloudifyAnsibleSDKError)

    _ctx.logger.debug('Output: {0}'.format(output))
    _ctx.logger.debug('Error: {0}'.format(error))
    _ctx.logger.debug('Return Code: {0}'.format(return_code))

    if return_code in UNREACHABLE_CODES:
        raise OperationRetry(
            'One or more hosts are unreachable.')
    if return_code not in SUCCESS_CODES:
        raise NonRecoverableError(
            'One or more hosts failed.')


@operation
@ansible_relationship_source
def ansible_requires_host(new_sources_dict, _ctx, **_):
    current_sources_dict = \
        _ctx.source.instance.runtime_properties.get(
            constants.SOURCES, {})
    current_sources = sources.AnsibleSource(current_sources_dict)
    new_sources = sources.AnsibleSource(new_sources_dict)
    current_sources.merge_source(new_sources)
    _ctx.source.instance.runtime_properties[constants.SOURCES] = \
        current_sources.config
