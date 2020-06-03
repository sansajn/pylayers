# journey database support
import sqlite3

def main():
	conn = sqlite3.connect('test/journey.db')
	cur = conn.cursor()

	# get list of stop names and infotainment codes
	line = 'U1'
	direction = 'A'
	result = cur.execute('SELECT stop_name_public, stop_number_infotainment_direction_0 FROM stops WHERE line_name=? AND direction=?',
		(line, direction))
	stops = result.fetchall()  # [(stop, code)]

	lines = cur.execute('SELECT DISTINCT line_name FROM stops').fetchall()
	print(lines)

	cur.close()
	conn.close()

if __name__ == '__main__':
	main()
