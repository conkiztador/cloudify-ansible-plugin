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

from cloudify import ctx as ctx_from_import

from cloudify_ansible.utils import (
    create_playbook_workspace,
    delete_playbook_workspace,
    handle_site_yaml,
    handle_sources,
    get_source_config_from_ctx
)


def ansible_relationship_source(func):
    def wrapper(group_name=None,
                hostname=None,
                host_config=None,
                ctx=ctx_from_import):
        source_dict = get_source_config_from_ctx(
            ctx, group_name, hostname, host_config)
        func(source_dict, ctx)
    return wrapper


def ansible_playbook_node(func):

    def wrapper(playbook_path=None,
                sources=None,
                ctx=ctx_from_import,
                ansible_env_vars=None,
                debug_level=2,
                additional_args=None,
                site_yaml_path=None,
                **kwargs):
        """Prepare the arguments to send to AnsiblePlaybookFromFile.

        :param site_yaml_path:
            The absolute or relative (blueprint) path to the site.yaml.
        :param sources: Either a path (with the site.yaml).
            Or a YAML dictionary (from the blueprint itself).
        :param ctx: The cloudify context.
        :param ansible_env_vars:
          A dictionary of environment variables to set.
        :param kwargs:
        :return:
        """

        playbook_path = playbook_path or site_yaml_path
        ansible_env_vars = \
            ansible_env_vars or {'ANSIBLE_HOST_KEY_CHECKING': "False"}
        sources = \
            sources or \
            get_source_config_from_ctx(ctx)

        create_playbook_workspace(ctx)
        playbook_path = handle_site_yaml(playbook_path, ctx)
        playbook_args = {
            'playbook_path': playbook_path,
            'sources': handle_sources(sources, playbook_path, ctx),
            'verbosity': debug_level,
            'additional_args': additional_args or '',
            'logger': ctx.logger
        }
        playbook_args.update(**kwargs)
        func(playbook_args, ansible_env_vars, ctx)
        delete_playbook_workspace(ctx)

    return wrapper
