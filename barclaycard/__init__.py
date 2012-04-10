"""Barclaycard ePDQ API interface"""

# Nick Snell <nick@orpo.co.uk>

import re
import requests

__version__ = '1.1'

# Defaults
EPDQ_ENDPOINT = 'https://secure2.epdq.co.uk/cgi-bin/CcxBarclaysEpdqEncTool.e'

# Currencies
EPDQ_CURRENCY_GBP = '826'

# Charge types
EPDQ_CHARGE_AUTH = 'Auth'
EPDQ_CHARGE_PREAUTH = 'PreAuth'

class BarclaycardEPDQException(Exception): pass

class BarclaycardEPDQ(object):
	
	def __init__(self, epdq_client_id, epdq_passphrase, charge_type=EPDQ_CHARGE_PREAUTH, 
				currency_code=EPDQ_CURRENCY_GBP, debug=False):
		"""Initalise the API interface"""
		
		self._epdq_client_id = epdq_client_id
		self._epdq_passphrase = epdq_passphrase
		
		self.currency_code = currency_code
		self.charge_type = charge_type
		
		self._debug = debug
		
	def _call(self, url=EPDQ_ENDPOINT, data=None, method='GET'):
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
		
		headers = {
			'User-Agent': 'Python-Barclaycard-eDPQ/%s' % __version__
		}
		
		response = None
		
		# Choose a method to contact the ePDQ
		if method == 'GET':
			response = requests.get(url, params=data, headers=headers)
			
		elif method == 'POST':
			# Set additional headers for a POST
			headers.update({
				'Content-Type': 	'application/x-www-form-urlencoded',
				'Content-Length':	str(len(data)),
				'Accept': 			'text/plain',
			})
			
			response = requests.get(url, data=data, headers=headers)
		
		if not response.status_code == 200:
			raise BarclaycardEPDQException('Unable to process request: %s received' % 
				response.status_code
			)
		
		return response.text
		
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
			value = re.findall('value="(.+?)"', response)[0]
		except (TypeError, IndexError):
			if self._debug:
				err_msg = 'Invalid response from ePDQ - %s' % response
			else:
				err_msg = 'Unable to process request, invalid response from ePDQ!'
			
			raise BarclaycardEPDQException(err_msg)
			
		return value
	
	def get_epdq_url(self):
		"""Return the full URL used for ePDQ transactions"""
		return EPDQ_ENDPOINT
