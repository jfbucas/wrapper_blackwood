# Global libs
import os
import time
import datetime
import threading
import ctypes


#
# This thread checks if the CPU should be left alone based on not "niced" CPU usage
#



CLOCK_TICKS = os.sysconf("SC_CLK_TCK")

class Leave_CPU_Alone():

	cpu_info = {}
	cpu_info[ 0 ] = {}
	cpu_info[ 1 ] = {}
	cpu_turn = 0
	period = 1

	last_answer = False

	PROCESS_CPU_THRESHOLD = 2.8

	def __init__( self, period=5 ):

		self.get_cpu_info( 0 )
		self.get_cpu_info( 1 )

		self.period  = period

	def get_cpu_info(self, turn=None ):

		if turn == None:
			turn = self.cpu_turn


		f = open('/proc/stat', 'rb')
		try:
			values = f.readline().split()
		finally:
			f.close()

		self.cpu_info[ turn ][ 0 ] = datetime.datetime.now()
		self.cpu_info[ turn ][ 1 ] = float(values[1]) / CLOCK_TICKS # User 


	def is_one_process_running( self ):
		self.get_cpu_info()

		# If the last reading is less than the time period old we prefer not to rush to any conclusion
		if (self.cpu_info[ self.cpu_turn ][ 0 ] - self.cpu_info[ 1 - self.cpu_turn ][ 0 ]) < datetime.timedelta(seconds=self.period):
			return self.last_answer

		v = (self.cpu_info[ self.cpu_turn ][ 1 ] - self.cpu_info[ 1 - self.cpu_turn ][ 1 ]) / self.period

		self.cpu_turn = 1 - self.cpu_turn
		self.last_answer = (v > self.PROCESS_CPU_THRESHOLD)
		return self.last_answer
	


class Leave_CPU_Alone_Thread(threading.Thread):

	lca = None
	period = 1
	stop_lca_thread = False

	def __init__(self, period=5): 
		threading.Thread.__init__(self)
		self.lca = Leave_CPU_Alone( period=period )
		self.period = period
		self.stop_lca_thread = False

	def run(self):

		if os.environ.get('NOLCA') != None:
			return
		
		while not self.stop_lca_thread:

			# 0 means it is not paused
			# 1 means it has been activated
			# 2 means it has been activated/forced manually

			if self.libblackwood.LibExt.getPause(self.libblackwood.cb) == 0:
				one_process = self.lca.is_one_process_running()
				if one_process:
					os.system("killall -SIGSTOP mono")
				else:
					os.system("killall -SIGCONT mono")

			time.sleep(self.period)
		


if __name__ == "__main__":

	lca = Leave_CPU_Alone(desktop=False)

	while True:
		print( lca.is_one_process_running() )
		print( lca.is_during_working_hours() )
		time.sleep(1)

