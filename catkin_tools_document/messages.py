# Copyright 2016 Clearpath Robotics Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re

from catkin_tools.common import mkdir_p


def _write_raw(f, msg_type):
    msg_text = re.split('^=+$', msg_type._full_text, maxsplit=1, flags=re.MULTILINE)[0]
    msg_text = re.sub('^(.*?)$', '    \\1', msg_text, flags=re.MULTILINE)
    f.write(msg_text)
    f.write('\n')


def generate_messages(logger, event_queue, package, package_path, output_path):
    try:
        msg_module = __import__(package.name + '.msg').msg
        msg_names = [ msg_name for msg_name in dir(msg_module)
                      if re.match('^[A-Z]', msg_name) ]
    except ImportError:
        msg_names = []

    if msg_names:
        with open(os.path.join(output_path, 'messages.rst'), 'w') as f:
            f.write('Messages\n')
            f.write('========\n')
            f.write("""
            .. toctree::
                :titlesonly:
                :glob:

                msg/*
            """)

        mkdir_p(os.path.join(output_path, 'msg'))
        for msg_name in msg_names:
            msg_type = getattr(msg_module, msg_name)
            with open(os.path.join(output_path, 'msg', '%s.rst' % msg_name), 'w') as f:
                f.write('%s\n' % msg_name)
                f.write('=' * (len(msg_name) + len(package.name) + 5) + '\n\n')
                f.write('Definition::\n\n')
                _write_raw(f, msg_type)

    return 0


def generate_services(logger, event_queue, package, package_path, output_path):
    try:
        srv_module = __import__(package.name + '.srv').srv
        srv_names = [ srv_name for srv_name in dir(srv_module)
                      if re.match('^[A-Z]', srv_name) ]
    except ImportError:
        srv_names = []

    if srv_names:
        with open(os.path.join(output_path, 'services.rst'), 'w') as f:
            f.write('Services\n')
            f.write('========\n')
            f.write("""
            .. toctree::
                :titlesonly:
                :glob:

                srv/*
            """)

        mkdir_p(os.path.join(output_path, 'srv'))
        for srv_name in srv_names:
            srv_type = getattr(srv_module, srv_name)
            if hasattr(srv_type, '_request_class'):
                with open(os.path.join(output_path, 'srv', '%s.rst' % srv_name), 'w') as f:
                    f.write('%s\n' % srv_name)
                    f.write('=' * 50 + '\n\n')
                    f.write('Request Definition::\n\n')
                    _write_raw(f, srv_type._request_class)
                    f.write('Response Definition::\n\n')
                    _write_raw(f, srv_type._response_class)
    return 0


def _get_person_links(people):
    person_links = []
    for person in people:
        if person.email:
            person_links.append("`%s <mailto:%s>`_" % (person.name, person.email))
        else:
            person_links.append(person.name)
    return person_links


def generate_package_summary(logger, event_queue, package, package_path,
                             rosdoc_conf, output_path):
    mkdir_p(output_path)
    with open(os.path.join(output_path, 'conf.py'), 'w') as f:
        f.write('project = %s\n' % repr(package.name))
        f.write('copyright = "Clearpath Robotics"\n')
        f.write('author = %s\n' % repr(', '.join([person.name for person in package.authors])))

        f.write("version = %s\n" % repr(package.version))
        f.write("release = %s\n" % repr(package.version))

        f.write("""
master_doc = 'index'
html_theme = 'agogo'

templates_path = []

#html_sidebars = {
#   '**': ['sidebartoc.html', 'sourcelink.html', 'searchbox.html']
#}
""")

    with open(os.path.join(output_path, 'index.rst'), 'w') as f:
        f.write('%s\n' % package.name)
        f.write('=' * 50 + '\n\n')

        f.write('**Authors:** %s\n\n' % ', '.join(_get_person_links(package.authors)))
        f.write('**Maintainers:** %s\n\n' % ', '.join(_get_person_links(package.maintainers)))

        f.write("""
.. toctree::
    :titlesonly:

""")
        for conf in rosdoc_conf:
            rosdoc_output_dir = conf.get('output_dir', 'html')
            f.write("    %s/index\n" % rosdoc_output_dir)
            mkdir_p(os.path.join(output_path, rosdoc_output_dir))
            with open(os.path.join(output_path, rosdoc_output_dir, 'index.rst'), 'w') as g:
                g.write("API Docs (%s)\n" % conf['builder'])
                g.write('=' * (len(conf['builder']) + 11) + '\n')

        if os.path.exists(os.path.join(output_path, 'messages.rst')):
            f.write("    messages\n")
        if os.path.exists(os.path.join(output_path, 'services.rst')):
            f.write("    services\n")
        if os.path.exists(os.path.join(output_path, 'actions.rst')):
            f.write("    actions\n")

        changelog_path = os.path.join(package_path, 'CHANGELOG.rst')
        changelog_symlink_path = os.path.join(output_path, 'CHANGELOG.rst')
        if os.path.exists(changelog_path) and not os.path.exists(changelog_symlink_path):
            os.symlink(changelog_path, changelog_symlink_path)

        if os.path.exists(changelog_symlink_path):
            f.write("    Changelog <CHANGELOG>\n")


    return 0

