__author__ = 'Kibur'

import sys
import random
import socket
import fcntl
import struct
import shlex, subprocess

class ChangeMAC:
	def setIface(self, iface):
		self.iface = iface

	def getIface(self):
		return self.iface

	def ifState(self, state):
		args = shlex.split('sudo ip link set dev ' + self.getIface() + ' ' + state)
		p = subprocess.Popen(args,\
			stdout=subprocess.PIPE,\
			stderr=subprocess.PIPE)
		out, err = p.communicate()

		print self.getIface() + ' ' + state

	def setDefaultGateway(self, defaultG):
		if defaultG is None:
			sys.exit('Failed gathering default-gateway')

		args = shlex.split('sudo ip route add default via ' + defaultG)
		p = subprocess.Popen(args,\
			stdout=subprocess.PIPE,\
			stderr=subprocess.PIPE)
		out, err = p.communicate()

	def getDefaultGateway(self):
		with open('/proc/net/route') as fh:
			for line in fh:
				fields = line.strip().split()

				if fields[1] != '00000000' or not int(fields[3], 16) & 2:
					continue

				return socket.inet_ntoa(struct.pack('=L', int(fields[2], 16)))

	def setMAC(self, MACaddr=None):
		print 'Previous MAC address ' + self.getHwAddr(self.getIface())

		if MACaddr is None: MACaddr = self.randomMAC()
		args = shlex.split('sudo ip link set dev ' + self.getIface() + ' address ' + MACaddr)
		p = subprocess.Popen(args,\
			stdout=subprocess.PIPE,\
			stderr=subprocess.PIPE)
		out, err = p.communicate()

		print 'New MAC address ' + MACaddr

	def getHwAddr(self, ifname):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))

		return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

	def randomMAC(self):
		return ':'.join(map(lambda x: "%02x" % x, [ 0x00, 0x0C, 0xF1, random.randint(0x00, 0xFF), random.randint(0x00, 0xFF), random.randint(0x00, 0xFF) ]))

	def __init__(self, iface='eth0'):
		self.iface = iface

class UI:
	def configurate(self, cm, dg, iface, MACaddr=None):
		cm.setIface(iface)
		cm.ifState('down')
		cm.setMAC(MACaddr)
		cm.ifState('up')
		cm.setDefaultGateway(dg)

	def __init__(self):
		cm = ChangeMAC()
		dg = cm.getDefaultGateway()

		if len(sys.argv) < 2:
			print 'Usage MAC-Gen <iface>'
			sys.exit('More info --help')
		else:
			if len(sys.argv) == 2:
				if sys.argv[1] == '--help':
					print 'Usage MAC-Gen <iface> [MAC addr]'
					print 'Example: MAC-Gen wlan0'
					print 'This will generate and set a MAC address for this interface'
					print
					print 'Example: MAC-Gen wlan0 00:16:3e:43:3d:a0'
					print 'This will set your chosen MAC address for this interface'
					sys.exit(0)
				else:
					self.configurate(cm, dg, sys.argv[1])
			elif len(sys.argv) == 3:
					self.configurate(cm, dg, sys.argv[1], sys.argv[2])

if __name__ == '__main__':
	ui = UI()
