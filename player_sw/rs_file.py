import json
from datetime import datetime

class rs_file:
	def __init__(self):
		self._d = {}  # raw data
		self._news = {}  # news spot content list
		self._fleet = {}
		self._stop = {}
		self._fallback = {}

	def open(self, fname):
		with open(fname) as fin:
			self._d = json.load(fin)

		for contlist in self._contlist():
			if contlist['category'] == 'sequence-static-address-character-only':
				self._news = contlist
			elif contlist['category'] == '2nd-sequence-static-address-character-only':
				self._fleet = contlist
			elif contlist['category'] == 'event-driven-dynamic-address-interpretation':
				self._stop = contlist
			elif contlist['category'] == 'fallback-sequence-position-independent-only':
				self._fallback = contlist
			else:
				print('warning: %s spot list ignored' % contlist['category'])

	def news(self):
		'''returns list of news spots'''
		spots = [spot(spot_record) for spot_record in self._news['spotitem']]
		return spots

	def fleet(self):
		'''returns list of fleet spots'''
		spots = [spot(spot_record) for spot_record in self._fleet['spotitem']]
		return spots

	def stop(self):
		'''returns list of stop spots'''
		spots = [spot(spot_record) for spot_record in self._stop['spotitem']]
		return spots

	def _contlist(self):
		return self._d['root']['cell']['crc']['machines'][0]['contlist']


class spot:
	def __init__(self, spot_record):
		self.id = spot_record['id']
		self.name = spot_record['name']
		self.valid_date = () # (from, to)
		self.line = []  # (number:string, direction:int)
		self.section = []  # (from:int, to:int)
		
		datetime.strptime(spot_record, '%Y-%M-%D')

		if 'spotitemaddress' in spot_record:
			address = spot_record['spotitemaddress']
			if 'line' in address:
				line = address['line']
				for num_dir in line:
					self.line.append((num_dir['number'], int(num_dir['direction'])))

			if 'section' in address:
				section = address['section']
				for from_to in section:
					self.section.append((int(from_to['from']), int(from_to['to'])))

	def is_addressed(self):
		return len(self.line) > 0 or len(self.section) > 0



def spot_on_journey(spot, journey):
	for from_to in spot.section:
		try:
			from_idx = journey.index(from_to[0])
			to_idx = journey.index(from_to[1], from_idx)
			return from_idx
		except ValueError:
			return -1

	return -1




if __name__ == '__main__':
	rs = rs_file()
	rs.open('test/rs.json')

	news = rs.news()
	print('news spots %d' % len(news))

	stop_list = rs.stop()
	print('stop spots %d' % len(stop_list))

	stop_code = 1009
	for stop_spot in stop_list:
		for from_to in stop_spot.section:
			if from_to[0] == stop_code:
				print(stop_spot.id, stop_spot.name)

	print('---')

	# print all spots on a journey
	journey = [1001, 1009, 1017, 1027, 1037, 1045, 1054]
	for spot in stop_list:
		idx = spot_on_journey(spot, journey)
		if idx != -1:
			print(idx, spot.id, spot.name)


