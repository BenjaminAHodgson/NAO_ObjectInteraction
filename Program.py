## Name: Benjamin Hodgson
## ID: 215120652
## Email: bhodgs@deakin.edu.au


import argparse
import time
import math
from naoqi import ALBroker, ALModule, ALProxy


nao = None
FRAME_TORSO = 0
FRAME_ROBOT = 2

#Class for an interactive NAO robot
class NaoMulti(ALModule):

    def __init__(self, ip, port, name="nao"):
        self.my_broker = ALBroker(
            "myBroker",
            "0.0.0.0",                                # listen to anyone
            0,                                        # find a free port and use it
            ip,                                       # parent broker IP
            port)                                     # parent broker port
        ALModule.__init__(self, name)
        self.name = name
        self.hand_full_threshold = 0.20 ## Adjust at demo if given chance.
        self.tts_service = ALProxy("ALTextToSpeech")
        self.memory_service = ALProxy("ALMemory")

        ## Defaults ##
        self.touched = False
        self.detected = False
        self.abort = False

    ## Get Current Posture
    def get_posture(self):
        posture_service = ALProxy("ALRobotPosture")
        posture = posture_service.getPostureFamily()
        print('posture')
        return posture

    ## Allows selection of NAO posture
    def go_to_posture(self, posture_name):
        posture_service = ALProxy("ALRobotPosture")
        result = posture_service.goToPosture(posture_name, 0.5)
        self.get_posture()
        return result

    ## This checks if the NAO robot is grasping something.
    def hand_full(self):
        motion_service = ALProxy("ALMotion")
        motion_service.setAngles("RHand", 0.0, 0.35)
        time.sleep(2.0)
        hand_angle = motion_service.getAngles("RHand", True)
        print(str(hand_angle))
 
        if hand_angle[0] < self.hand_full_threshold:
            result = False
            self.tts_service.say("Nothing in my hand.")
        else:
            self.tts_service.say("I detect a ball in my hand.")
            result = True
        return result

    ## Moves relative to it's frame.
    def move(self, destination):
        x = destination[0]
        y = destination[1]
        theta = math.atan(y / x)
        motion_service = ALProxy("ALMotion")
        motion_service.moveInit()
        motion_service.moveTo(x, y, theta)
        self.tts_service.say('Movement Complete')

    def take_ball(self):
        print('Taking Ball')
        names = ["RShoulderPitch", "RWristYaw", "RElbowYaw", "RHand"]
        angles = [0.441, 1.815, 1.335, 1.00]
        fraction_max_speed = 0.2

        ## Incorps: wait_redball() &&  redball_follower() ##
        self.wait_redball()
        self.tts_service.say("I see the ball")
        self.redball_follower(True)
        ##                                                ##

        time.sleep(2.0)

        motion_service = ALProxy("ALMotion")
        motion_service.setStiffnesses("RArm", 1.0)
        motion_service.setAngles(names, angles, fraction_max_speed)
        time.sleep(1.0)
        self.memory_service.subscribeToEvent("HandRightBackTouched", self.name, "hand_touched")
        self.memory_service.subscribeToEvent("MiddleTactilTouched", self.name, "middle_tactil_abort")

        timer = 0
        while self.touched == False:
            time.sleep(1.0)
            timer+= 1
            if timer > 40:
                self.memory_service.raiseEvent("MiddleTactilTouched", 1.0)

        self.touched = False
        self.redball_follower(False)
        motion_service.setAngles("RHand", 0.00, 0.25)
        time.sleep(2.0)
        names = names[0:3]
        angles = [1.47, 0.11, 1.20]
        motion_service.setAngles(names, angles, fraction_max_speed)
        time.sleep(2.0)
        motion_service.setStiffnesses("RArm", 0.0)

    def give_ball(self):
        names = ["RShoulderPitch", "RWristYaw", "RElbowYaw"]
        angles = [0.441, 1.815,1.335]
        fraction_max_speed = 0.2
        motion_service = ALProxy("ALMotion")
        motion_service.setStiffnesses("RArm", 1.0)
        motion_service.setAngles(names, angles, fraction_max_speed)
        time.sleep(2.0)
        motion_service.setAngles("RHand", 1.00, fraction_max_speed)
        self.memory_service.subscribeToEvent("HandRightBackTouched", self.name, "hand_touched")
        self.memory_service.subscribeToEvent("MiddleTactilTouched", self.name, "middle_tactil_abort")
        self.touched = False

        timer = 0
        while self.touched == False:
            time.sleep(1.0)
            timer+= 1
            if timer > 40:
                self.memory_service.raiseEvent("MiddleTactilTouched", 1.0)

        self.touched = False
        self.go_to_posture("Stand")

    ## Waits until red ball is detected.
    def wait_redball(self):
        self.memory_service.subscribeToEvent("redBallDetected", self.name, "redball_detected")
        self.memory_service.subscribeToEvent("MiddleTactilTouched", self.name, "middle_tactil_abort")
        timer = 0
        while self.detected == False and self.abort == False:
            time.sleep(1)
            self.detected = False
            timer+= 1
            if timer > 60:
                self.memory_service.raiseEvent("MiddleTactilTouched", 1.0)

    ## Follows red ball with head
    def redball_follower(self, ready, mode="Head"):
        tracker = ALProxy("ALTracker")
        motion_service = ALProxy("ALMotion")
        motion_service.wakeUp()
        ## FIX: APP CRASH
        self.go_to_posture("Stand")
        if ready:
            tracker.registerTarget(self.target_name, self.diameter_ball)
            tracker.setMode(mode)
            tracker.setEffector("None")
            tracker.track(self.target_name)
        else:
            tracker.stopTracker()
            tracker.unregisterAllTargets()
    
    ## Looks for ball
    def find_ball(self):
        tracker = ALProxy("ALTracker")
        self.target_name = "RedBall"
        self.diameter_ball = input('Please enter the diameter of the ball (in meters): ')
        if self.diameter_ball == "":
            self.diameter_ball = 0.07
        tracker.registerTarget(self.target_name, self.diameter_ball)
        tracker.setMode("Move")
        tracker.setEffector("None")
        tracker.track(self.target_name)
        self.tts_service.say("Please present the ball.")
        too_far = True
        tracker.toggleSearch(True)
        while too_far:
            position = tracker.getTargetPosition(FRAME_ROBOT)
            if position != []:
                #Trig to get distance
                distance = math.sqrt(math.pow(position[0],2) + math.pow(position[1],2))
                print(str(position))
                print(str(distance))
                if distance < 0.25:
                    too_far = False
                    tracker.stopTracker()
                    tracker.unregisterAllTargets()
                    print("Tracker: Target reached")
        too_far=True
        time.sleep(1.0)
        self.tts_service.say("Found Red Ball.")

    # case: event triggered, response: unsubscribe #

    def redball_detected(self, event_name, value):
        print("Event raised: " + event_name + " " + str(value))
        self.memory_service.unsubscribeToEvent("redBallDetected", self.name)
        self.not_detected = False

    def hand_touched(self, event_name, value):
        print("Event raised: " + event_name + " " + str(value))
        self.memory_service.unsubscribeToEvent("HandRightBackTouched", self.name)
        self.touched = False

    def middle_tactil_abort(self, event_name, value):
        print("Event raised: " + event_name + " " + str(value))
        self.memory_service.unsubscribeToEvent("MiddleTactilTouched", self.name)
        self.abort = True

    # call at end of sequence #
    def disconnect(self):
        self.my_broker.shutdown()
        print("Broker shut down.")

    def switch_activity(self):
        select = { 'find_ball': self.find_ball, 'take_ball': self.take_ball, 'give_ball': self.give_ball, }
        choice = input('Manually run a function: ')
        print('Running: ' + choice)
        select[choice]()





def main():
    ## setup ##
    ip = input('Enter the IP of your robot: ')
    port = int(input('Enter the port of your robot: '))

    ## organise nao object ##
    global nao
    nao = NaoMulti(ip, port)

    try:
        while True:
            nao.switch_activity()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Stopping...")
        nao.disconnect()

if __name__ == "__main__":
    main()
