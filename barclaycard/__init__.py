"""Barclaycard ePDQ API interface"""

# Nick Snell <nick@orpo.co.uk>
# 7th November 2011

import re
import httplib
import urllib
import urlparse

__version__ = '1.0'

# Defaults
EPDQ_ENDPOINT = 'secure2.epdq.co.uk'
EPDQ_URL = '/cgi-bin/CcxBarclaysEpdqEncTool.e'

# Currencies
EPDQ_CURRENCY_GBP = '826'

# Charge types
EPDQ_CHARGE_AUTH = 'Auth'
EPDQ_CHARGE_PREAUTH = 'PreAuth'

class BarclaycardEPDQException(Exception): pass

class BarclaycardEPDQ(object):
	
	def __init__(self, epdq_client_id, epdq_passphrase, charge_type=EPDQ_CHARGE_PREAUTH, 
				currency_code=EPDQ_CURRENCY_GBP):
		"""Initalise the API interface"""
		
		self._epdq_client_id = epdq_client_id
		self._epdq_passphrase = epdq_passphrase
		
		self.currency_code = currency_code
		self.charge_type = charge_type
		
	def _call(self, url=EPDQ_URL, data=None, method='GET'):
		"""Call the API and return the response"""
		
		if method not in ('GET', 'POST'):
			raise BarclaycardEPDQException('Unsupported method "%s" sent to ePDQ interface!' % method)
		
		if data is None:
			raise BarclaycardEPDQException('No data sent to ePDQ interface!')
		
		# Add defaults
		data.update({
			'clientid':			self._epdq_client_id,
			'password':			self._epdq_passphrase,
			'chargetype':		self.charge_type,
			'currency_code':	self.currency_code,
		})
		
		# Setup any arguments we are sending to 
		data = urllib.urlencode(data)
		
		headers = {
			'User-Agent': 'Python-Barclaycard-eDPQ/%s' % __version__
		}
		
		# Setup a connection to ePDQ
		connection = httplib.HTTPSConnection(EPDQ_ENDPOINT)
		
		response = None
		
		# Choose a method to contact the ePDQ
		if method == 'GET':
			# Build the GET URL
			url = '%s?%s' % (url, data)
			
			connection.request(method, url, None, headers)
			response = connection.getresponse()
			
		elif method == 'POST':
			# Set additional headers for a POST
			headers.update({
				'Content-Type': 	'application/x-www-form-urlencoded',
				'Content-Length':	len(data),
				'Accept': 			'text/plain',
			})
			
			connection.request(method, url, data, headers)
			response = connection.getresponse()
		
		# Tidy up
		connection.close()
		
		if not response.status == 200:
			raise BarclaycardEPDQException('Unable to process request: %s %s' % (
				response.status, 
				response.reason
			))
		
		return response
		
	def get_epdq_key(self, total, order_ref=None):
		"""Get a ePDQ encryption key"""
		
		# Setup the data for the key request
		data = {
			'total':	str(total),
		}
		
		if order_ref is not None:
			data['oid'] = order_ref
		
		# Call the API
		response = self._call(data=data, method='POST')
		
		# Try to parse the response
		# Comes back in the format: <INPUT name=epdqdata type=hidden value="...some value...">
		try:
			# Attempt to use a regex to get the value we want - first match wins
			value = re.findall('value="(.+?)"', response.read())[0]
		except (TypeError, IndexError):
			raise BarclaycardEPDQException('Unable to process request, invalid response from ePDQ!')
			
		return value
	
	def get_epdq_url(self):
		"""Return the full URL used for ePDQ transactions"""
		return urlparse.urljoin('http://%s' % EPDQ_ENDPOINT, EPDQ_URL)
