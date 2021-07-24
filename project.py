import RPi.GPIO as GPIO
import time
import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

GPIO.setwarnings(False)

C = 262
D = 294
E = 330
F = 349
G = 392
A = 440
B = 494

led = 20
piezo = 13
motor = 17
pinTrigger = 0
pinEcho = 1

max = 10.5
min = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(led, GPIO.OUT)
GPIO.setup(piezo, GPIO.OUT)
GPIO.setup(motor, GPIO.OUT)
GPIO.setup(pinTrigger, GPIO.OUT)
GPIO.setup(pinEcho, GPIO.IN)

pwm_piezo = GPIO.PWM(piezo, 1.0)
pwm_motor = GPIO.PWM(motor, 50)
pwm_motor.start(max)

melody = [E,D,C,D,E,E,E,D,D,D,E,E,E,E,D,C,D,E,E,E,D,D,E,D,C]
warning = [349, 392]


class Thread_piezo(QThread):
	threadEvent = pyqtSignal(int)

	def __init__(self, parent = None):
		super().__init__()
		self.n = 0
		self.main = parent
		self.isRun = False

	def run(self):
		pwm_piezo.ChangeFrequency(10)
		while self.isRun:
			pwm_piezo.ChangeFrequency(melody[self.n])
			time.sleep(0.3)
			self.threadEvent.emit(self.n)
			self.n += 1
			if self.n > 24:
				self.n = 0
	#			break

#		pwm_piezo.stop()

#####################################

class Thread_sonic(QThread):
	threadEvent = pyqtSignal(int)

	def __init__(self, parent = None):
		super().__init__()
		self.n = 0
		self.main = parent
		self.isRun = False

	def run(self):
		pwm_piezo.ChangeFrequency(10)
		while self.isRun:
			GPIO.output(pinTrigger, True)
			time.sleep(0.0001)
			GPIO.output(pinTrigger, False)

			start = time.time()

			while GPIO.input(pinEcho) == False:
				start = time.time()
			while GPIO.input(pinEcho) == True:
				stop = time.time()

			elapsed = stop - start
			distance = (elapsed*19000)/2

			if  distance > 15:
				print("safe")
				time.sleep(1)
			elif 10 < distance <= 15:
				pwm_piezo.ChangeFrequency(warning[0])
				time.sleep(0.4)
				pwm_piezo.ChangeFrequency(warning[1])
				time.sleep(0.4)
				print("Distance : %.2f cm" %distance)
			elif 5 < distance <= 10:
				pwm_piezo.ChangeFrequency(warning[0])
				time.sleep(0.2)
				pwm_piezo.ChangeFrequency(warning[1])
				time.sleep(0.2)
				print("Distance : %.2f cm" %distance)
			elif 1 <= distance <= 5:
				pwm_piezo.ChangeFrequency(warning[0])
				time.sleep(0.05)
				pwm_piezo.ChangeFrequency(warning[1])
				time.sleep(0.05)
				print("Distance : %.2f cm" %distance)
############################################

class myWindow(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.ui = uic.loadUi("project.ui", self)
		self.ui.show()

		self.th1 = Thread_piezo(self)
		self.th3 = Thread_sonic(self)
		self.th1.daemon = True
		self.th3.daemon = True
		self.th1.threadEvent.connect(self.threadEventHandler)
		self.th3.threadEvent.connect(self.threadEventHandler)

	def threadEventHandler(self,n): pass

	def led_on(self):
		self.ui.label.setText("LED ON")
		GPIO.output(led,True)

	def led_off(self):
		self.ui.label.setText("LED OFF")
		GPIO.output(led,False)

	def exit(self):
		print("<End the Program >")
		GPIO.output(led,False)
		sys.exit()

	def piezo_on(self):
		print("Play Music")
		self.ui.label.setText("Music ON")
		pwm_piezo.start(50.0)
		if not self.th1.isRun:
			self.th1.isRun = True
			self.th1.start()

	def piezo_off(self):
		print("Stop Music")
		self.ui.label.setText("Music OFF")
		if self.th1.isRun:
			self.th1.isRun = False
		pwm_piezo.stop()

	def motor_dial(self):
		dial = self.ui.lcdNumber.value()
		avg = max + (((min-max)/180)*dial)
		pwm_motor.ChangeDutyCycle(avg)
		
	def decrease(self):
		motor_dial = self.ui.lcdNumber.value()-5
		print("Down")
		self.ui.label.setText("Down")
		if motor_dial < 0: 
			pass
		else:
			pwm_motor.ChangeDutyCycle(12)
			self.ui.dial.setValue(motor_dial)

	def increase(self):
		motor_dial = self.ui.lcdNumber.value()+5
		print("UP")
		self.ui.label.setText("UP")
		if motor_dial > 180 : 
			pass
		else:
			pwm_motor.ChangeDutyCycle(12)
			self.ui.dial.setValue(motor_dial)

	
	def sonic_on(self):
		print("sonic ON")
		self.ui.label.setText("Sonic ON")
		pwm_piezo.start(50.0)
		if not self.th3.isRun:
			self.th3.isRun = True
			self.th3.start()

	def sonic_off(self):
		print("sonic OFF")
		self.ui.label.setText("Sonic OFF")
		if self.th3.isRun:
			self.th3.isRun = False
		pwm_piezo.stop()

	def slot_dial(self):
		motor_dial = self.ui.lcdNumber.value()
		pwm_motor.ChangeDutyCycle(motor_dial/18)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	myapp = myWindow()
	app.exec_()

pwm_piezo.ChangeDutyCycle(0.0)
pwm_piezo.stop()
pwm_motor.stop()

GPIO.cleanup()
