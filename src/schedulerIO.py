import curses
import curses.textpad
import os
import time



def padTabs(str):
	str = ' ' + str
	while len(str) < 20:
		str += ' '
	return(str)


def progBar(perc, l):
	str = '|'
	n = int(perc * (l - 2))
	while len(str) < (l - 1):
		if n > 0:
			str = str + '#'
			n -= 1
		else: str = str + ' '
	str = str + '|'
	return(str)



class SchedulerIO:
	def __init__(self, sched):
		self.sched = sched
		self.shutdownT = False
		self.shutdownTimer = 100

		self.stdscr = curses.initscr()
		self.stdscr.keypad(1)
		self.stdscr.nodelay(1)
		curses.noecho()
		curses.cbreak()

		# SET COLORS
		curses.start_color()
		curses.init_color(20, 400, 400, 400);
		# unselected tab
		curses.init_pair(1, curses.COLOR_BLACK, 20)
		# selected tab
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
		curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)

		# SET PARAMETERS
		self.winTabs = ['Log', 'Schedule', 'Status']
		self.currTab = 0
		self.logScrollState = 0
		self.jobScrollState = 0
		self.instScrollState = 0

		# SET WIN DIM
		# windows should be at least 360 wide x 240 tall??
		self.winH = self.stdscr.getmaxyx()[0]
		self.winW = self.stdscr.getmaxyx()[1]

		# INITIALIZE SUB WIN
		# tabs
		self.tabWin = curses.newwin(1, self.winW, 0, 0)
		
		# main win
		self.mainWin = curses.newwin(self.winH - 2, self.winW, 1, 0)
		
		# command win
		self.inWin = curses.newwin(1, self.winW, self.winH - 1, 0)
		self.inTextBox = curses.textpad.Textbox(self.inWin)
		self.inWin.nodelay(1)

		self.stdscr.refresh()

		while not self.shutdownT or self.shutdownTimer > 0:
			self.mainWin.erase()

			if self.shutdownT:
				self.shutdownTimer -= 1

			self.mainWin.erase()

			c = self.stdscr.getch()
			if c == ord(':'):
				cmd = self.inTextBox.edit()
				try:
					if self.runCmd(cmd.strip()) == 1:
						self.sched.addLog('>> command invalid: {0}'.format(cmd))
				except Exception as e:
					self.sched.addLog('>> command encountered exception: {0}'.format(e))
				self.inWin.erase()

			if c == curses.KEY_RIGHT:
				self.currTab = (self.currTab + 1) % len(self.winTabs)
			if c == curses.KEY_LEFT:
				self.currTab = (self.currTab - 1) % len(self.winTabs)

			self.dispTabs()
			if self.currTab == 0: self.dispLog()
			elif self.currTab == 1: self.dispSchedule()
			elif self.currTab == 2: self.dispStatus()

			self.tabWin.refresh()
			self.mainWin.refresh()
			self.inWin.refresh()
			time.sleep(0.2)
		curses.endwin()


	def dispTabs(self):
		for i in range(len(self.winTabs)):
			if i == self.currTab: self.tabWin.addstr(0, i * 20, padTabs(self.winTabs[i]), curses.color_pair(2))
			else: self.tabWin.addstr(0, i * 20, padTabs(self.winTabs[i]), curses.color_pair(1))
		return(0)


	def dispStatus(self):
		self.mainWin.addstr(0, 0, 'RUNNING STATUS', curses.A_BOLD | curses.A_UNDERLINE)

		self.mainWin.addstr(1, 4, 'downloader ', curses.A_BOLD)
		self.mainWin.addstr(1, 15, 'is ')
		if self.sched.pausedDownloadT or self.sched.pausedT:
			self.mainWin.addstr(1, 18, 'paused', curses.color_pair(3))
		else: self.mainWin.addstr(1, 18, 'running', curses.color_pair(4))

		self.mainWin.addstr(2, 4, 'extractor ', curses.A_BOLD)
		self.mainWin.addstr(2, 14, 'is ')
		if self.sched.pausedExtractT or self.sched.pausedT:
			self.mainWin.addstr(2, 17, 'paused', curses.color_pair(3))
		else: self.mainWin.addstr(2, 17, 'running', curses.color_pair(4))

		self.mainWin.addstr(4, 0, 'SCHEDULER STATISTICS', curses.A_BOLD | curses.A_UNDERLINE)


	def dispLog(self):
		logItems = [i[:self.winW] for i in self.sched.log[-(self.winH - 2):]]
		for i in range(len(logItems)):
			self.mainWin.addstr(i, 0, logItems[i])
		return(0)


	def dispSchedule(self):
		self.mainWin.addstr(0, 0, 'AUTO DOWNLOAD QUEUE', curses.A_BOLD | curses.A_UNDERLINE)
		self.mainWin.addstr(0, 80, 'MANUAL DOWNLOAD QUEUE', curses.A_BOLD | curses.A_UNDERLINE)
		self.mainWin.addstr(0, 160, 'EXTRACTION QUEUE', curses.A_BOLD | curses.A_UNDERLINE)
		
		autoDownloadQueue = self.sched.d_queue_auto[:self.winH / 5]
		manDownloadQueue = self.sched.d_queue_man[:self.winH / 5]
		extQueue = self.sched.e_queue[:self.winH / 5]

		yn = 0
		for task in autoDownloadQueue:
			self.dispSingleDownload(task, yn * 5 + 2, 0)
			yn += 1

		yn = 0
		for task in manDownloadQueue:
			self.dispSingleDownload(task, yn * 5 + 2, 80)
			yn += 1

		yn = 0
		for task in extQueue:
			self.dispSingleExtraction(task, yn * 5 + 2, 160)
			yn += 1
		return(0)


	def dispSingleDownload(self, task, y, x):
		self.mainWin.addstr(y, x, 'sceneid: ', curses.A_BOLD)
		self.mainWin.addstr(y, x + 9, task.id)
		self.mainWin.addstr(y + 1, x, 'location: ' + 'NULL')
		if task.status == 'PENDING':
			self.mainWin.addstr(y + 2, x, 'pending download', curses.color_pair(3))
		else:
			prog = float(task.status.prog)/task.status.tot
			self.mainWin.addstr(y + 2, x, 'downloading', curses.color_pair(4))
			self.mainWin.addstr(y + 3, x, progBar(prog, 75))


	def dispSingleExtraction(self, task, y, x):
		self.mainWin.addstr(y, x, 'sceneid: ', curses.A_BOLD)
		self.mainWin.addstr(y, x + 9, task.id)
		self.mainWin.addstr(y + 1, x, 'location: ' + 'NULL')
		if task.status == 'PENDING':
			self.mainWin.addstr(y + 2, x, 'pending extraction', curses.color_pair(3))
		else:
			prog = float(task.status.prog)/task.status.tot
			self.mainWin.addstr(y + 2, x, 'extracting', curses.color_pair(4))
			self.mainWin.addstr(y + 3, x, progBar(prog, 75))
		return(0)


	def runCmd(self, cmd):
		cmdspl = cmd.split()
		if cmdspl[0] == 'shutdown':
			self.currTab = 0 # changes to log window
			self.shutdownT = True
			self.sched.shutdown()
			return(0)

		if cmdspl[0] == 'pause':
			if len(cmdspl) == 1:
				self.sched.pausedT = not self.sched.pausedT
				if self.sched.pausedT:
					self.sched.addLog('scheduler paused')
				else: self.sched.addLog('scheduler unpaused')
				return(0)

			if cmdspl[1] == 'extract':
				self.sched.pausedExtractT = not self.sched.pausedExtractT
				if self.sched.pausedExtractT:
					self.sched.addLog('extractor paused')
				else: self.sched.addLog('extractor unpaused')
				return(0)

			if cmdspl[1] == 'download':
				self.sched.pausedDownloadT = not self.sched.pausedDownloadT
				if self.sched.pausedDownloadT:
					self.sched.addLog('downloader paused')
				else: self.sched.addLog('downloader unpaused')
				return(0)

		# Implement manual scene insertion=
		return(1)