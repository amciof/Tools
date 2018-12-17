from threading import Thread
from queue     import Queue


class Task:
	FINISH       = -1
	CREATE_LABEL = +1

class Worker(Thread):

	def __init__(self, outQueue, file):
		Thread.__init__(self)

		self.outQueue  = outQueue
		self.taskQueue = Queue()

		self.file = open(file, 'w')
		

	def free(self):

		self.file.close()


	def run(self):
		while True:
			i = 0
			while i < 10000000:
				i += 1

			task = self.taskQueue.get(block=True)
			
			if task == Task.FINISH:
				break;
			elif task == Task.CREATE_LABEL:
				self.file.write('Label')
				self.outQueue.put(self.getName())


	def addTask(self, task):

		self.taskQueue.put(task)


outQueue = Queue()

w1 = Worker(outQueue, 'w1.txt')
w2 = Worker(outQueue, 'w2.txt')

w1.start()
w2.start()

while True:
	print('Continue?')
	answer = input()
	if answer == 'y':
		print('Choose thread(1/2)')

		answer = input()
		if answer == '1':
			w1.addTask(Task.CREATE_LABEL)
		elif answer == '2':
			w2.addTask(Task.CREATE_LABEL)
		else:
			print('Bad input')

	elif answer == 'n':
		w1.addTask(Task.FINISH)
		w2.addTask(Task.FINISH)
		break;

	else:
		print('Bad input')

while not outQueue.empty():
	print(outQueue.get())

w1.free()
w2.free()