#!/usr/bin/env python
# 
# Copyright 2010 Google Inc. All Rights Reserved.
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

"""Module to help with updating InstallLog schema with new applesus property.

This file is completely unneeded if you're starting with a clean and empty
InstallLog model in Datastore.

Previously models.InstallLog was designed to only hold Munki pkg installs. With
the introduction of Apple SUS integration, Apple SUS and Munki installs were
both stored in InstallLog, but there wasn't a way to tell them apart so an
'applesus' boolean property was added to InstallLog.

This module contains two functions that help with the switch from the InstallLog
without the applesus property to the newer InstallLog with the property.
  SetAppleSUSBoolean: loop through a list of known Apple installs and set any
      InstallLog entities to applesus=True.

  TouchAllInstalls: call put() on all entities so the applesus entity isn't missing, so reports that filter('applesus', bool) don't omit such entities.

Both of these functions should be called from the interactive console using
deferred.
"""





import logging
from google.appengine.ext import deferred
from simian.mac import models


# This list is generated with the following code:
#   import models
#   counts, _ =  models.ReportsCache.GetInstallCounts()
#   for k in sorted(counts.keys()):
#     if counts[k]['applesus']:
#       print '    u\'%s\': True,' % k.encode('utf-8')
APPLE_SUS_INSTALLS = {
    u'2009 Aluminum Keyboard Firmware Update-1.0': True,
    u'AirMac ユーティリティ-5.5.2': True,
    u'AirPort Utility-5.5.2': True,
    u'AirPort Utility-5.5.3': True,
    u'Aluminum Keyboard Firmware Update-1.1': True,
    u'Aluminum Keyboard Software Update-2.0': True,
    u'Aperture Update-2.1.4': True,
    u'Aperture Update-3.1.1': True,
    u'Aperture Update-3.1.2': True,
    u'Aperture Update-3.1.3': True,
    u'Atualização de Segurança 2010-007-1.0': True,
    u'Basic TeX 2008-1.3.0.0.0': True,
    u'Bluetooth Firmware Update-2.0.1': True,
    u'Bluetooth Firmware-Aktualisierung-2.0.1': True,
    u'Bluetooth ファームウェア・アップデート-2.0.1': True,
    u'Brother Printer Drivers Update-1.1': True,
    u'Brother Printer Software Update-2.4': True,
    u'Brother Printer Software Update-2.5': True,
    u'Brother Printer Software Update-2.6': True,
    u'Brother Printer Software Update-2.7': True,
    u'Canon Printer Software Update-2.3': True,
    u'Canon Printer Software Update-2.4.1': True,
    u'Canon Printer Software Update-2.5': True,
    u'Canon Printer Software Update-2.6': True,
    u'Cinema Tools Update-4.0.1': True,
    u'DVD Player-4.6': True,
    u'DVD Studio Pro Update-4.2.1': True,
    u'Digital Camera Raw Compatibility Update-2.7': True,
    u'Digital Camera Raw Compatibility Update-3.5': True,
    u'Digital Camera Raw Compatibility Update-3.6': True,
    u'Digital Camera Raw Compatibility Update-3.7': True,
    u'Display Camera Firmware Update-1.0': True,
    u'EPSON Printer Drivers Update-1.0': True,
    u'EPSON Printer Software Update-2.5.1': True,
    u'EPSON Printer Software Update-2.6': True,
    u'EPSON Printer Software Update-2.7': True,
    u'EPSON Printer Software Update-2.8': True,
    u'Final Cut Express HD Update-3.5.1': True,
    u'Final Cut Express Update-4.0.1': True,
    u'Final Cut Pro Update-6.0.6': True,
    u'Final Cut Pro X Supplemental Content-1.0': True,
    u'Front Row Update-2.1.7': True,
    u'Fuji Xerox Printer Software Update-2.1': True,
    u'GarageBand Instruments and Apple Loops-1.0': True,
    u'GarageBand Update-3.0.2': True,
    u'GarageBand Update-3.0.4': True,
    u'GarageBand Update-3.0.5': True,
    u'GarageBand Update-4.1.1': True,
    u'GarageBand Update-4.1.2': True,
    u'GarageBand Update-5.1': True,
    u'GarageBand Update-6.0.1': True,
    u'GarageBand Update-6.0.2': True,
    u'GarageBand Update-6.0.4': True,
    u'GarageBand 更新-6.0.2': True,
    u'Gecombineerde Mac OS X-update-10.6.7': True,
    u'Gestetner Printer Drivers Update-2.0': True,
    u'Gestetner Printer Software Update-2.1': True,
    u'HP Printer Drivers Update-1.1.1': True,
    u'HP Printer Software Update-2.4.1': True,
    u'HP Printer Software Update-2.5.2': True,
    u'HP Printer Software Update-2.6': True,
    u'HP Printer Software Update-2.7': True,
    u'Java for Mac OS X 10.5 Update 10-1.0': True,
    u'Java for Mac OS X 10.5 Update 5-1.0': True,
    u'Java for Mac OS X 10.5 Update 8-1.0': True,
    u'Java for Mac OS X 10.5 Update 9-1.0': True,
    u'Java for Mac OS X 10.5 アップデート 8-1.0': True,
    u'Java for Mac OS X 10.6 Update 2-1.0': True,
    u'Java for Mac OS X 10.6 Update 3-1.0': True,
    u'Java for Mac OS X 10.6 Update 4-1.0': True,
    u'Java for Mac OS X 10.6 Update 5-1.0': True,
    u'Java for Mac OS X 10.6 アップデート 3-1.0': True,
    u'Java for Mac OS X 10.6 アップデート 5-1.0': True,
    u'Java für Mac OS X 10.5 Update 8-1.0': True,
    u'Java für Mac OS X 10.5 Update 9-1.0': True,
    u'Keyboard Firmware Update-1.0': True,
    u'Keynote Update-3.0.1v2': True,
    u'Keynote Update-4.0.4': True,
    u'LED Cinema Display Firmware Update-1.0': True,
    u'Lanier Printer Software Update-2.1': True,
    u'Leistungs-Update-1.0': True,
    u'Lexmark Printer Software Update-2.3.1': True,
    u'Lexmark Printer Software Update-2.4': True,
    u'Lexmark Printer Software Update-2.5': True,
    u'Lexmark Printer Software Update-2.6': True,
    u'Lion Recovery Update-1.0': True,
    u'Logic Express Update-9.1.4': True,
    u'Logic Express-8.0.2': True,
    u'Logic Express-9.1.3': True,
    u'Logic Pro Update-9.1.4': True,
    u'Logic Pro Update-9.1.5': True,
    u'Logic Pro-8.0.2': True,
    u'Logic Pro-9.1.3': True,
    u'Mac OS X 10.6.7 Update for MacBook Pro (Early 2011)-1.0': True,
    u'Mac OS X 10.6.8 Supplemental Update-1.0': True,
    u'Mac OS X 10.6.8 追加アップデート-1.0': True,
    u'Mac OS X Update Combined-10.6.6': True,
    u'Mac OS X Update Combined-10.6.7': True,
    u'Mac OS X Update Combined-10.6.8': True,
    u'Mac OS X Update Combined-10.6.8 v1.1': True,
    u'Mac OS X Update-10.5.8': True,
    u'Mac OS X Update-10.6.4': True,
    u'Mac OS X Update-10.6.5': True,
    u'Mac OS X Update-10.6.6': True,
    u'Mac OS X Update-10.6.7': True,
    u'Mac OS X Update-10.6.8': True,
    u'Mac OS X Update-10.6.8 v1.1': True,
    u'Mac OS X Update-10.7.1': True,
    u'Mac OS X v10.6.7 Supplemental Update for 13\" MacBook Air (Late 2010)-1.0': True,
    u'Mac Pro EFI Firmware Update-1.1': True,
    u'Mac Pro EFI Firmware Update-1.2': True,
    u'Mac Pro EFI Firmware Update-1.3': True,
    u'Mac Pro EFI Firmware Update-1.4': True,
    u'Mac Pro EFI Firmware Update-1.5': True,
    u'Mac Pro SMC Firmware Update-1.1': True,
    u'MacBook Air EFI Firmware Update-1.0': True,
    u'MacBook Air EFI Firmware Update-2.0': True,
    u'MacBook Air SMC Firmware Update-1.2': True,
    u'MacBook Air (Late 2010) Software Update-2.0': True,
    u'MacBook EFI Firmware Update-1.1': True,
    u'MacBook EFI Firmware Update-1.2': True,
    u'MacBook EFI Firmware Update-1.4': True,
    u'MacBook Pro EFI Firmware Update-1.2': True,
    u'MacBook Pro EFI Firmware Update-1.4': True,
    u'MacBook Pro EFI Firmware Update-1.5.1': True,
    u'MacBook Pro EFI Firmware Update-1.7': True,
    u'MacBook Pro EFI Firmware Update-1.8': True,
    u'MacBook Pro EFI Firmware Update-1.9': True,
    u'MacBook Pro EFI Firmware Update-2.0': True,
    u'MacBook Pro EFI Firmware Update-2.1': True,
    u'MacBook Pro EFI Firmware Update-2.2': True,
    u'MacBook Pro SMC Firmware Update-1.3': True,
    u'MacBook Pro SMC Firmware Update-1.4': True,
    u'MacBook Pro Software Update 1.4-1.4': True,
    u'MacBook Pro Software Update-1.3': True,
    u'MacBook SMC Firmware Update-1.4': True,
    u'MacTeX_Additions-1.3.0.0.0': True,
    u'Magic Trackpad and Multi-Touch Update-1.0': True,
    u'MainStage Update-1.0.2': True,
    u'MainStage Update-2.1.3': True,
    u'MainStage-2.0.1': True,
    u'MainStage-2.1.2': True,
    u'Migration Assistant Update for Mac OS X Leopard-1.0': True,
    u'Migration Assistant Update for Mac OS X Snow Leopard-1.0': True,
    u'Mini DisplayPort to VGA Firmware Update-1.0': True,
    u'Motion Supplemental Content-1.0': True,
    u'Motion Update-3.0.2': True,
    u'NRG Printer Drivers Update-2.0': True,
    u'Numbers Update-1.0.3': True,
    u'Pages Update-2.0.1v2': True,
    u'Pages Update-3.0.3': True,
    u'Performance Update-1.0': True,
    u'PlugIn-10.1.102.64.0': True,
    u'PlugIn-10.2.152.26': True,
    u'PlugIn-10.2.153.1': True,
    u'PluginManager Update-1.7.3': True,
    u'PluginManager-1.7.3': True,
    u'Pro Applications Update 2005-01-1.1': True,
    u'Pro Applications Update 2006-01-1.0': True,
    u'Pro Applications Update 2006-02-1.0': True,
    u'Pro Applications Update 2007-01-1.0': True,
    u'Pro Applications Update 2008-05-1.0': True,
    u'Pro Applications Update 2010-02-1.0': True,
    u'ProApps QuickTime codecs-1.0': True,
    u'ProKit Update-6.0.1': True,
    u'ProKit Update-7.0': True,
    u'QuickTime 7.6.9 for Leopard-7.6.9.1.1187990468': True,
    u'QuickTime-7.6.9': True,
    u'QuickTime-7.6.9.1.1187990468': True,
    u'QuickTime-7.7': True,
    u'Remote Desktop Admin Update-2.2': True,
    u'Remote Desktop Admin Update-3.4': True,
    u'Remote Desktop Admin Update-3.5': True,
    u'Remote Desktop Client Update-3.4': True,
    u'Remote Desktop Client Update-3.5.1': True,
    u'Remote Desktop Connection-12.1.0.0.0': True,
    u'Remote Desktop クライアントアップデート-3.4': True,
    u'Ricoh Printer Software Update-2.1': True,
    u'Rosetta-1.0': True,
    u'Safari-5.0': True,
    u'Safari-5.0.2': True,
    u'Safari-5.0.3': True,
    u'Safari-5.0.4': True,
    u'Safari-5.0.5': True,
    u'Safari-5.0.6': True,
    u'Safari-5.1': True,
    u'Safari-5.1.1': True,
    u'Samsung Printer Software Update-2.1': True,
    u'Samsung Printer Software Update-2.2': True,
    u'Security Update 2010-003-1.0': True,
    u'Security Update 2010-005-1.0': True,
    u'Security Update 2010-006-1.0': True,
    u'Security Update 2010-007-1.0': True,
    u'Security Update 2011-001-1.0': True,
    u'Security Update 2011-002-1.0': True,
    u'Security Update 2011-003-1.0': True,
    u'Security Update 2011-004-1.0': True,
    u'Security Update 2011-005-1.0': True,
    u'Security Update 2011-006-1.0': True,
    u'Server Admin Tools-10.6.5': True,
    u'Server Admin Tools-10.6.7': True,
    u'Server Admin Tools-10.6.8': True,
    u'Sicherheitsupdate 2010-007-1.0': True,
    u'Sikkerhetsoppdatering 2010-007-1.0': True,
    u'Snow Leopard Font Update-1.0': True,
    u'Snow Leopard Graphics Update-1.0': True,
    u'Soundtrack Pro Update-2.0.2': True,
    u'SuperDrive Firmware Update-3.0': True,
    u'Thunderbolt Display Firmware-1.0': True,
    u'Thunderbolt Firmware Update-1.0': True,
    u'Thunderbolt Software Update-1.0': True,
    u'Update Ricoh-printersoftware-2.1': True,
    u'Uppdatering 9 av Java för Mac OS X 10.5-1.0': True,
    u'Utilitário AirPort-5.5.2': True,
    u'VoiceOver Kit for iPod-1.4': True,
    u'WaveBurner-1.6.1': True,
    u'Wireless Mouse Software Update-1.0': True,
    u'Xcode Update-3.2.3': True,
    u'Xcode Update-3.2.4': True,
    u'Xcode Update-3.2.5': True,
    u'Xcode Update-3.2.6': True,
    u'Xerox Printer Software Update-2.1': True,
    u'iDVD 7.1.1 Update-7.1.1': True,
    u'iDVD 7.1.2-7.1.2': True,
    u'iDVD Extra Content-1.0': True,
    u'iDVD Update-6.0.4': True,
    u'iDVD Update-7.0.4': True,
    u'iLife Support-9.0.4': True,
    u'iMovie 9.0.1-9.0.1': True,
    u'iMovie 9.0.2-9.0.2': True,
    u'iMovie 9.0.4-9.0.4': True,
    u'iMovie HD Combo Update-6.0.2': True,
    u'iMovie HD Update-6.0.3': True,
    u'iMovie Update-7.1': True,
    u'iMovie Update-7.1.4': True,
    u'iMovie Update-8.0.6': True,
    u'iPhone Configuration Utility-3.2': True,
    u'iPhone Configuration Utility-3.3': True,
    u'iPhone Configuration Utility-3.4': True,
    u'iPhone SDK Compatibility Update-1.0': True,
    u'iPhoto 9.1.1-9.1.1': True,
    u'iPhoto 9.1.2-9.1.2': True,
    u'iPhoto 9.1.3-9.1.3': True,
    u'iPhoto 9.1.5-9.1.5': True,
    u'iPhoto Update-6.0.4': True,
    u'iPhoto Update-6.0.5': True,
    u'iPhoto Update-6.0.6': True,
    u'iPhoto Update-7.1': True,
    u'iPhoto Update-7.1.4': True,
    u'iPhoto Update-7.1.5': True,
    u'iPhoto Update-8.1': True,
    u'iPhoto Update-8.1.2': True,
    u'iPhoto Update-9.1': True,
    u'iTunes-10': True,
    u'iTunes-10.0.1': True,
    u'iTunes-10.1.1': True,
    u'iTunes-10.1.2': True,
    u'iTunes-10.2': True,
    u'iTunes-10.2.0.0': True,
    u'iTunes-10.2.1': True,
    u'iTunes-10.2.2': True,
    u'iTunes-10.3': True,
    u'iTunes-10.3.1': True,
    u'iTunes-10.4': True,
    u'iTunes-10.4.1': True,
    u'iTunes-10.5': True,
    u'iTunes-9.1.1': True,
    u'iTunes-9.2': True,
    u'iTunes-9.2.1': True,
    u'iWeb Update-2.0.3': True,
    u'iWeb Update-2.0.4': True,
    u'iWeb Update-3.0.2': True,
    u'iWeb Update-3.0.3': True,
    u'iWeb Update-3.0.4': True,
    u'iWork Update 4-9.0.4': True,
    u'iWork Update 5-9.0.5': True,
    u'iWork Update 6-9.1': True,
    u'iWork アップデート 5-9.0.5': True,
    u'セキュリティアップデート 2010-007-1.0': True,
    u'パフォーマンスアップデート-1.0': True,
    u'移行アシスタント for Mac OS X Snow Leopard-1.0': True,
    u'보안 업데이트 2011-002-1.0': True,
}


def SetAppleSUSBoolean():
  """Sets applesus=True all InstallLog entities that are Apple SUS installs."""
  MAX = 2000
  updates = APPLE_SUS_INSTALLS.keys()
  updates.sort()
  for key in updates:
    logging.debug('Querying for: %s', key)
    q = models.InstallLog.all().filter(
        'package =', key).filter('applesus =', False)
    i = 0
    cursor = None
    while True:
      if cursor:
        logging.debug('Continuing with cursor: %s', cursor)
        q.with_cursor(cursor)
      entities = q.fetch(MAX)
      if not entities:
        logging.debug('%s updated. No remaining %s', i, key)
        break
      for e in entities:
        i += 1
        e.applesus = True
        e.put()

        if i == MAX:
          logging.info('%s entities converted', i)
          break
      if i > 0:
        cursor = q.cursor()


def TouchAllInstalls(cursor=None):
  """Touches all InstallLog entities so the new applesus property is created."""
  more = True
  q = models.InstallLog.all()
  i = 0
  while True:
    more = True
    if cursor:
      logging.debug('Continuing with cursor: %s', cursor)
      q.with_cursor(cursor)
    entities = q.fetch(2000)
    if not entities:
      logging.debug('%s updated. No remaining %s', i, key)
      more = False
      break
    for e in entities:
      i += 1
      e.put()

    cursor = q.cursor()
    if i >= 4000:
      logging.info('%s entities converted', i)

  if more:
    deferred.defer(TouchAllInstalls, cursor=cursor)