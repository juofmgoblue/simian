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

"""Manifest Modifications admin handler."""




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


class ManifestModifications(webapp.RequestHandler):
  """Handler for /admin/manifest_modifications."""

  def post(self):
    """POST handler."""
    if not auth.IsAdminUser():
      self.response.set_status(403)
      return

    if self.request.get('add_manifest_mod'):
      self._AddManifestModification()
    elif self.request.get('enabled'):
      self._ToggleManifestModification()
    else:
      self.response.set_status(404)

  def _AddManifestModification(self):
    """Adds a new manifest modification to Datastore."""
    # TODO(user): add support for other types of manifest modifications.
    owner = self.request.get('owner').strip()
    munki_pkg_name = self.request.get('munki_pkg_name').strip()
    manifests = self.request.get_all('manifests')
    install_types = self.request.get_all('install_types')

    # Validation.
    error_msg = None
    if not owner or not munki_pkg_name or not install_types:
      error_msg = 'owner, munki_pkg_name, and install_types are all required'
    if not error_msg:
      for manifest in manifests:
        if manifest not in common.TRACKS:
          error_msg = 'manifest %s is not in %s' % (manifest, common.TRACKS)
    if not error_msg:
      for install_type in install_types:
        if install_type not in common.INSTALL_TYPES:
          error_msg = 'install_type %s is not in %s' % (
              install_type, common.INSTALL_TYPES)
    if not error_msg:
      if not models.PackageInfo.all().filter('name =', munki_pkg_name).get():
        error_msg = 'No package found with Munki name: %s' % munki_pkg_name
    if error_msg:
      self.redirect('/admin/manifest_modifications?error=%s' % error_msg)
      return

    mod = models.OwnerManifestModification(
        key_name='%s##%s' % (owner, munki_pkg_name),
        owner=owner, value=munki_pkg_name, manifests=manifests,
        install_types=install_types, user=users.get_current_user())
    mod.put()
    self.redirect('/admin/manifest_modifications')

  def _ToggleManifestModification(self):
    """Toggles manifest modifications between enabled and disabled."""
    key_str = self.request.get('key')
    enabled = self.request.get('enabled') == '1'
    mod = db.get(db.Key(key_str))
    mod.enabled = enabled
    mod.put()
    data = {'enabled': enabled, 'key': key_str}
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(util.Serialize(data))

  def get(self, report=None, product_id=None):
    """GET handler."""
    auth.DoUserAuth()
    self._DisplayMain()

  def _DisplayMain(self):
    """Displays the main Manifest Modification report."""
    # TODO(user): Allow for ?mod_type=foo for owner/site/os_version/etc mods.
    mods = models.OwnerManifestModification.all().order('-mtime')
    error = self.request.get('error')
    is_admin = auth.IsAdminUser()
    # TODO(user): generate PackageInfo dict so admin select box can use display
    #             names, munki package names can link to installs, etc.
    if is_admin:
      munki_pkg_names = [e.name for e in models.PackageInfo.all()]
    else:
      munki_pkg_names = None


    data = {
      'mods': mods,
      'error': error,
      'is_admin': is_admin,
      'munki_pkg_names': munki_pkg_names,
      'install_types': common.INSTALL_TYPES,
      'manifests': common.TRACKS,
    }
    self.response.out.write(
        RenderTemplate('templates/manifest_modifications.html', data))


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