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

"""Module dealing with machine UUIDs.

MachineUuid: class to hold machine UUID properties.
"""



import re

class Error(Exception):
  """Base error."""


class GenerateMachineUuidError(Error):
  """Machine UUID cannot be generated by supplied info, it is unknown."""


class MachineUuid(object):
  """Class to load machine information and generate a uuid.

  uuid is generated in the format

  VARIABLE=VALUE

  Possible variables are:

  eth:
  value will be MAC address, format lowercase, exactly 2 hex digits per octet

  hwid:
  value will be a string, unknown case or formatting

  Examples:

  eth=00:01:02:03:04:05
  hwid=SomeValue
  """

  REGEX = {
    'eth': re.compile(r'^([0-9A-F]{2}:){5}([0-9A-F]{2})$', re.IGNORECASE),
    'hwid': re.compile(r'^[^_]+$'),
  }

  PAIR_SET = '='

  def __init__(self):
    """Init."""
    self._properties = {
        'eth': [],   # list of MAC addresses
        'hwid': '',  # a serial number or other UUID from the OS
    }

  def GetProperties(self):
    """Return all properties as dictionary."""
    return self._properties

  def _CheckPropertyValue(self, prop_name, value):
    """Check a property value against regex.

    Args:
      prop_name: str, property name
      value: obj, value to set
    Raises:
      ValueError: if value is malformed
    """
    if prop_name in self.REGEX:
      if not self.REGEX[prop_name].match(value):
        raise ValueError(prop_name, value)

  def _SetGenericList(self, prop_name, list_idx, value, default_value=None):
    """Set a property value where the property is a list.

    Args:
      prop_name: str, property name
      list_idx: int, index in property value to set
      value: obj, value to set
      default_value: obj, default value to use when expanding list size
    Raises:
      ValueError: if value is malformed
    """
    self._CheckPropertyValue(prop_name, value)
    if len(self._properties[prop_name]) > list_idx:
      self._properties[prop_name][list_idx] = value
    elif len(self._properties[prop_name]) == list_idx:
      self._properties[prop_name].append(value)
    else:
      self._properties[prop_name].extend(
          [default_value] * (list_idx-len(self._properties[prop_name])))
      self._properties[prop_name].append(value)

  def _SetGenericString(self, prop_name, value):
    """Set a string value in properties.

    Args:
      prop_name: str, property name
      value: str, value
    Raises:
      ValueError: if value is malformed
    """
    self._CheckPropertyValue(prop_name, value)
    self._properties[prop_name] = value

  def SetEthernetMac(self, n, mac_addr):
    """Set ethernet adapter MAC address.

    Args:
      n: int, adapter number, starting at 0
      mac_addr: str, in format "HH:HH:HH:HH:HH:HH"
    """
    self._SetGenericList('eth', n, mac_addr.lower())

  def SetWirelessMac(self, n, mac_addr):
    """Set wireless adapter MAC address.

    Args:
      n: int, adapter number, starting at 0
      mac_addr: str, in format "HH:HH:HH:HH:HH:HH"
    """
    self._SetGenericList('eth', n, mac_addr.lower())

  def SetHardwareId(self, hardware_id):
    """Set an arbitary machine hardware ID.

    Args:
      hardware_id: str, some type of machine hardware ID, e.g. a serial #
    """
    self._SetGenericString('hwid', hardware_id)

  def _GenerateMachinePropertyUuid(self, prop_name, value):
    """Returns the machine uuid string for one property."""
    return '%s%s%s' % (prop_name, self.PAIR_SET, value)

  def GenerateMachineUuid(self):
    """Returns the generated machine uuid.

    Returns:
      string like "eth=00:0..." or "hwid=XXX...", see class documentation.
    Raises:
      GenerateMachineUuidError: an error occured
    """
    value = None
    prop_name = None

    for i in xrange(len(self._properties['eth'])):
      if self._properties['eth'][i]:
        value = self._properties['eth'][i]
        prop_name = 'eth'
        break

    if not prop_name:
      if self._properties['hwid']:
        value = self._properties['hwid']
        prop_name = 'hwid'

    if prop_name and value:
      return self._GenerateMachinePropertyUuid(prop_name, value)
    else:
      raise GenerateMachineUuidError('Insufficient machine information')