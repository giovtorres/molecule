#  Copyright (c) 2015-2016 Cisco Systems
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import re

import pytest

from molecule import ansible_galaxy
from molecule import config


@pytest.fixture()
def galaxy_instance(temp_files):
    confs = temp_files(fixtures=['molecule_vagrant_config'])
    c = config.Config(configs=confs)
    c.config['ansible']['requirements_file'] = 'requirements.yml'

    return ansible_galaxy.AnsibleGalaxy(c.config)


def test_add_env_arg(galaxy_instance):
    galaxy_instance.add_env_arg('MOLECULE_1', 'test')

    assert 'test' == galaxy_instance.env['MOLECULE_1']


def test_install(mocker, galaxy_instance):
    mocked = mocker.patch('molecule.ansible_galaxy.AnsibleGalaxy.execute')
    galaxy_instance.install()

    mocked.assert_called_once

    # NOTE(retr0h): The following is a somewhat gross test, but need to
    # handle **kwargs expansion being unordered.
    pieces = str(galaxy_instance.galaxy).split()
    expected = ['--force', '--role-file=requirements.yml',
                '--roles-path=test/roles']

    assert re.search(r'ansible-galaxy', pieces[0])
    assert 'install' == pieces[1]
    assert expected == sorted(pieces[2:])


def test_install_overrides(mocker, galaxy_instance):
    galaxy_instance._config['ansible']['galaxy'] = {'foo': 'bar',
                                                    'force': False}
    mocked = mocker.patch('molecule.ansible_galaxy.AnsibleGalaxy.execute')
    galaxy_instance.install()

    mocked.assert_called_once

    pieces = str(galaxy_instance.galaxy).split()
    expected = ['--foo=bar', '--role-file=requirements.yml',
                '--roles-path=test/roles']

    assert expected == sorted(pieces[2:])