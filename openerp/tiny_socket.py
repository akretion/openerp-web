###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import socket
import cPickle
import marshal

DNS_CACHE = {}

class Myexception(Exception):
	def __init__(self, faultCode, faultString):
		self.faultCode = faultCode
		self.faultString = faultString
		self.args = (faultCode, faultString)

class mysocket:
	def __init__(self, sock=None):
		if sock is None:
			self.sock = socket.socket(
			socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.sock = sock
		self.sock.settimeout(120)
	def connect(self, host, port=False):
		if not port:
			protocol, buf = host.split('//')
			host, port = buf.split(':')
		if host in DNS_CACHE:
			host = DNS_CACHE[host]
		self.sock.connect((host, int(port)))
		DNS_CACHE[host], port = self.sock.getpeername()
	def disconnect(self):
		self.sock.shutdown(socket.SHUT_RDWR)
		self.sock.close()
	def mysend(self, msg, exception=False, traceback=None):
		msg = cPickle.dumps([msg,traceback])
		size = len(msg)
		self.sock.send('%8d' % size)
		self.sock.send(exception and "1" or "0")
		totalsent = 0
		while totalsent < size:
			sent = self.sock.send(msg[totalsent:])
			if sent == 0:
				raise RuntimeError, "socket connection broken"
			totalsent = totalsent + sent
	def myreceive(self):
		buf=''
		while len(buf) < 8:
			chunk = self.sock.recv(8 - len(buf))
			if chunk == '':
				raise RuntimeError, "socket connection broken"
			buf += chunk
		size = int(buf)
		buf = self.sock.recv(1)
		if buf != "0":
			exception = buf
		else:
			exception = False
		msg = ''
		while len(msg) < size:
			chunk = self.sock.recv(size-len(msg))
			if chunk == '':
				raise RuntimeError, "socket connection broken"
			msg = msg + chunk
		res = cPickle.loads(msg)
		if isinstance(res[0],Exception):
			if exception:
				raise Myexception(str(res[0]), str(res[1]))
			raise res[0]
		else:
			return res[0]
		
# vim: ts=4 sts=4 sw=4 si et

