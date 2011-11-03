#!/usr/bin/env python
# 
# Copyright 2011 Google Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# #
#

"""Package Alias admin handler."""




import logging
import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from simian.mac import models
from simian.mac import common
from simian.mac.common import auth
from simian.mac.common import util


class PackageAlias(webapp.RequestHandler):
  """Handler for /admin/package_alias."""

  def post(self):
    """POST handler."""
    if not auth.IsAdminUser():
      self.response.set_status(403)
      return

    if self.request.get('create_package_alias'):
      self._CreatePackageAlias()
    elif self.request.get('enabled'):
      self._TogglePackageAlias()
    else:
      self.response.set_status(404)

  def _CreatePackageAlias(self):
    """Creates a new or edits an existing package alias, with verification."""
    package_alias = self.request.get('package_alias').strip()
    munki_pkg_name = self.request.get('munki_pkg_name').strip()

    if not package_alias:
      self.redirect('/admin/package_alias?error=package_alias is required')
      return

    if not models.PackageInfo.all().filter('name =', munki_pkg_name).get():
      self.redirect(
          '/admin/package_alias?error=%s does not exist' % munki_pkg_name)
      return

    alias = models.PackageAlias(
        key_name=package_alias, munki_pkg_name=munki_pkg_name)
    alias.put()
    self.redirect('/admin/package_alias')

  def _TogglePackageAlias(self):
    """Sets an existing PackageAlias as enabled/disabled."""
    key_name = self.request.get('key_name')
    enabled = self.request.get('enabled') == '1'
    alias = models.PackageAlias.get_by_key_name(key_name)
    alias.enabled = enabled
    alias.put()
    data = {'enabled': enabled, 'key_name': key_name}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(util.Serialize(data))

  def get(self, report=None, product_id=None):
    """GET handler."""
    auth.DoUserAuth()
    self._DisplayMain()

  def _DisplayMain(self):
    """Displays the main Package Alias report."""
    package_aliases = models.PackageAlias.all()
    is_admin = auth.IsAdminUser()
    # TODO(user): generate PackageInfo dict so admin select box can use display
    #             names, munki package names can link to installs, etc.
    if is_admin:
      munki_pkg_names = [e.name for e in models.PackageInfo.all()]
    else:
      munki_pkg_names = None

    data = {
      'package_aliases': package_aliases,
      'error': self.request.get('error'),
      'is_admin': is_admin,
      'munki_pkg_names': munki_pkg_names,
    }
    self.response.out.write(
        RenderTemplate('templates/package_alias.html', data))


def RenderTemplate(template_path, values):
  """Renders a template using supplied data values and returns HTML.

  Args:
    template_path: str path of template.
    values: dict of template values.
  Returns:
    str HTML of rendered template.
  """
  path = os.path.join(
      os.path.dirname(__file__), template_path)
  return template.render(path, values)