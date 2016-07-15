import numpy as np
from Logic             import RobotVision as rv
from Logic.Global      import printf, wait
from Logic.LogicObject import LogicObject

"""
Example Class Structure
EVERY COMMAND MUST RETURN FALSE IF IT FAILS TO RUN
If it fails to run, return False. The idea is that users will know that any command will return false if it fails,
and thus have contingencies. Plus its a feature that is useful only if you know about it, and doesn't add complexity
otherwise!

class NameCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(NameCommand, self).__init__(parameters)

        # Load any objects, modules, calibrations, etc  that will be used in the run Section here. Use getVerifyXXXX()
        self.robot   = self.getVerifyRobot(env)
        self.vision  = self.getVerifyVision(env)

        if len(self.errors): return

        # Here, start tracking if your command requires it
        # Add any objects to be tracked

    def run(self):
        printf("A quick description, usually using parameters, of the command that is running")
        return True
"""



class Command(LogicObject):
    def __init__(self, parameters):
        super(Command, self).__init__()
        self.parameters = parameters

    def run(self):
        pass


#   BASIC CONTROL COMMANDS
class MoveXYZCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(MoveXYZCommand, self).__init__(parameters)

        # Load necessary objects
        self.interpreter = interpreter
        self.robot       = self.getVerifyRobot(env)

    def run(self):
        newX, successX = self.interpreter.evaluateExpression(self.parameters['x'])
        newY, successY = self.interpreter.evaluateExpression(self.parameters['y'])
        newZ, successZ = self.interpreter.evaluateExpression(self.parameters['z'])

        printf("Moving robot to ", newX, " ", newY, " ", newZ, " ")

        if successX and successY and successZ:
            self.robot.setPos(x=newX, y=newY, z=newZ, relative=self.parameters['relative'])
            return True
        else:
            printf("ERROR in parsing either X Y or Z: ", successX, successY, successZ)
            return False


class MoveWristCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(MoveWristCommand, self).__init__(parameters)

        self.interpreter = interpreter
        self.robot       = self.getVerifyRobot(env)

    def run(self):


        newAngle, success = self.interpreter.evaluateExpression(self.parameters['angle'])

        if success:
            # If relative, get the current wrist angle then add that to newAngle

            printf("Moving robot wrist to ", newAngle)
            self.robot.setServoAngles(servo3=newAngle, relative=self.parameters['relative'])
            return True
        else:
            printf("ERROR in parsing new wrist angle. Expression: ", self.parameters['angle'])
            return False


class PlayMotionRecordingCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(PlayMotionRecordingCommand, self).__init__(parameters)

        # Load any objects, modules, calibrations, etc  that will be used in the run Section here. Use getVerifyXXXX()
        self.robot       = self.getVerifyRobot(env)
        self.pathObj     = self.getVerifyObject(env, self.parameters["objectID"])
        self.interpreter = interpreter
        self.exitFunc    = interpreter.isExiting

        if len(self.errors): return

        self.motionPath = self.pathObj.getMotionPath()

    def run(self):
        if len(self.errors): return

        printf("Playing motionPath ", self.parameters["objectID"])

        # Evaluate the "Speed" variable
        newSpeed, success = self.interpreter.evaluateExpression(self.parameters['speed'])


        if not success or newSpeed <= 0:
            printf("ERROR: In evaluating 'speed' parameter for motionpath")
            return False

        # Since x2 should mean twice as fast, and .5 should mean twice as slow, inverse the speed
        newSpeed = 1.0 / newSpeed


        # Multiply the motionPath by newSpeed, to change how fast it replays
        mp = np.asarray(self.motionPath[:])
        time = mp[:, [0]] * newSpeed
        actions = mp[:, 1:]

        # If reversed, flip the "actions" array
        if self.parameters["reversed"]:
            actions = actions.tolist()
            actions = np.flipud(actions)  # Reverse the actions

        # Put the "time" and "actions" array back together and return it to a list
        mp = np.hstack((time, actions))
        mp.tolist()


        # Send the path to the "path player"
        rv.playMotionPath(mp.tolist(), self.robot, self.exitFunc)
        return True


class SpeedCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(SpeedCommand, self).__init__(parameters)

        # Load any objects that will be used in the run Section here
        self.robot       = env.getRobot()
        self.interpreter = interpreter

    def run(self):
        speed, success = self.interpreter.evaluateExpression(self.parameters['speed'])

        printf("Setting robot speed to ", speed, "cm/s")

        # Split the wait into incriments of 0.1 seconds each, and check if the thread has been stopped at each incriment
        if success:
            printf("Setting speed to ", speed)
            self.robot.setSpeed(speed)
            return True
        else:
            printf("ERROR: Expression ", self.parameters['speed'], " failed to evaluate correctly!")
            return False


class DetachCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(DetachCommand, self).__init__(parameters)

        self.robot = self.getVerifyRobot(env)

    def run(self):
        printf("Detaching servos ",
               self.parameters['servo1'],
               self.parameters['servo2'],
               self.parameters['servo3'],
               self.parameters['servo4'])


        printf("Detaching certain servos")
        if self.parameters['servo1']: self.robot.setActiveServos(servo0=False)
        if self.parameters['servo2']: self.robot.setActiveServos(servo1=False)
        if self.parameters['servo3']: self.robot.setActiveServos(servo2=False)
        if self.parameters['servo4']: self.robot.setActiveServos(servo3=False)

        return True


class AttachCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(AttachCommand, self).__init__(parameters)

        self.robot = self.getVerifyRobot(env)

    def run(self):
        printf("Attaching servos ", self.parameters['servo1'],
                                                         self.parameters['servo2'],
                                                         self.parameters['servo3'],
                                                         self.parameters['servo4'])

        printf("Attaching certain servos")
        if self.parameters['servo1']: self.robot.setActiveServos(servo0=True)
        if self.parameters['servo2']: self.robot.setActiveServos(servo1=True)
        if self.parameters['servo3']: self.robot.setActiveServos(servo2=True)
        if self.parameters['servo4']: self.robot.setActiveServos(servo3=True)

        return True


class WaitCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(WaitCommand, self).__init__(parameters)

        self.interpreter = interpreter

    def run(self):

        waitTime, success = self.interpreter.evaluateExpression(self.parameters['time'])


        # Split the wait into incriments of 0.1 seconds each, and check if the thread has been stopped at each incriment
        if success:
            printf("Waiting for", waitTime, "seconds")
            wait(waitTime, self.interpreter.isExiting)

            return True
        else:
            printf("ERROR: Expression ", self.parameters['time'], " failed to evaluate correctly!")
            return False


class GripCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(GripCommand, self).__init__(parameters)

        self.robot = self.getVerifyRobot(env)

    def run(self):
        printf("Setting gripper to True")
        self.robot.setGripper(True)
        return True


class DropCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(DropCommand, self).__init__(parameters)

        self.robot = self.getVerifyRobot(env)

    def run(self):
        printf("Setting gripper to False")
        self.robot.setGripper(False)
        return True


class BuzzerCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(BuzzerCommand, self).__init__(parameters)

        # Load any objects that will be used in the run Section here
        self.robot       = self.getVerifyRobot(env)
        self.interpreter = interpreter

    def run(self):

        frequency, fSuccess = self.interpreter.evaluateExpression(self.parameters['frequency'])
        duration,  dSuccess = self.interpreter.evaluateExpression(self.parameters['time'])

        # Check if evaluation worked
        if fSuccess and dSuccess:
            # Send buzzer command
            printf("Playing frequency", self.parameters['frequency'], " for ", self.parameters['time'])
            self.robot.setBuzzer(frequency, duration)

            # If the user wants to sleep while the buzzer is running, then sleep.
            if self.parameters["waitForBuzzer"]:
                wait(duration, self.interpreter.isExiting)

            return True
        else:
            printf("ERROR: ", self.parameters['frequency'],
                   " or ", self.parameters["time"], "failed to evaluate correctly!")
            return False


class EndProgramCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(EndProgramCommand, self).__init__(parameters)

    def run(self):
        printf("Attempting to shut down program now...")
        return "Kill"


class EndEventCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(EndEventCommand, self).__init__(parameters)

        # Load any objects that will be used in the run Section here
        self.interpreter = interpreter


    def run(self):
        printf("Exiting current event")
        return "Exit"





#   Robot + Vision Commands
class MoveRelativeToObjectCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(MoveRelativeToObjectCommand, self).__init__(parameters)

        self.interpreter = interpreter
        # Load any objects that will be used in the run Section here
        self.robot      = self.getVerifyRobot(env)
        self.vision     = self.getVerifyVision(env)
        self.trackable  = self.getVerifyObject(env, self.parameters["objectID"])
        coordCalib      = self.getVerifyCoordCalibrations(env)


        if len(self.errors): return
        self.ptPairs = coordCalib["ptPairs"]

        # Turn on tracking for the relevant object
        self.vision.addTarget(self.trackable)

    def run(self):
        if len(self.errors) > 0: return False

        newX, successX = self.interpreter.evaluateExpression(self.parameters['x'])
        newY, successY = self.interpreter.evaluateExpression(self.parameters['y'])
        newZ, successZ = self.interpreter.evaluateExpression(self.parameters['z'])


        # If X Y and Z could not be evaluated correctly, quit
        if not (successX and successY and successZ):
            printf("ERROR in parsing either X Y or Z: ", successX, successY, successZ)
            return False

        printf("Moving robot to obj, relative XYZ is:  ", newX, " ", newY, " ", newZ)


        # Get a super recent frame of the object
        trackedObj = self.vision.getObjectBruteAccurate(self.trackable,
                                                        minPoints   = rv.MIN_POINTS_FOCUS,
                                                        maxFrameAge = rv.MAX_FRAME_AGE_MOVE)
        if trackedObj is None: return False

        # Get the object position
        printf("Found object. Moving to XY Location now.")
        pos = rv.getPositionTransform(trackedObj.center, self.ptPairs, direction=1)


        # Set the robots position
        self.robot.setPos(x=pos[0] + newX, y=pos[1] + newY, z=pos[2] + trackedObj.view.height + newZ)
        return True


class PickupObjectCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(PickupObjectCommand, self).__init__(parameters)

        # Load any objects that will be used in the run Section here
        coordCalib      = self.getVerifyCoordCalibrations(env)
        self.robot      = self.getVerifyRobot(env)
        self.vision     = self.getVerifyVision(env)
        self.trackable  = self.getVerifyObject(env, self.parameters["objectID"])
        self.rbMarker   = self.getVerifyObject(env, "Robot Marker")
        self.exitFunc   = interpreter.isExiting

        if len(self.errors): return

        self.ptPairs    = coordCalib["ptPairs"]
        self.grndHeight = coordCalib["groundPos"][2]

        # Turn on tracking for the relevant object
        self.vision.addTarget(self.trackable)
        self.vision.addTarget(self.rbMarker)

    def run(self):
        if len(self.errors) > 0: return False

        ret = rv.pickupObject(self.trackable, self.rbMarker, self.ptPairs, self.grndHeight, self.robot, self.vision, self.exitFunc)

        return ret


class TestObjectSeenCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(TestObjectSeenCommand, self).__init__(parameters)

        # Load any objects, modules, calibrations, etc  that will be used in the run Section here. Use getVerifyXXXX()
        self.vision  = self.getVerifyVision(env)
        self.trackable = self.getVerifyObject(env, self.parameters["objectID"])


        if len(self.errors): return

        self.vision.addTarget(self.trackable)


        self.maxAge = self.parameters["age"]
        self.minPts = self.vision.planeTracker.MIN_MATCH_COUNT * (self.parameters["ptCount"] + 1)

    def run(self):
        if len(self.errors): return

        printf("Testing if ", self.parameters["objectID"], " was seen")
        tracked = self.vision.searchTrackedHistory(trackable  = self.trackable,
                                                   maxAge= self.maxAge,
                                                   minPtCount = self.minPts)

        # Return if an object that matched that criteria was tracked
        if self.parameters["not"]:
            return tracked is None
        else:
            return tracked is not None


class TestObjectLocationCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(TestObjectLocationCommand, self).__init__(parameters)

        # Load any objects, modules, calibrations, etc  that will be used in the run Section here. Use getVerifyXXXX()
        self.vision    = self.getVerifyVision(env)
        self.trackable = self.getVerifyObject(env, self.parameters["objectID"])
        vStream   = self.getVerifyVStream(env)


        if len(self.errors): return
        self.vision.addTarget(self.trackable)

        # Get the dimensions of the frame
        frame = vStream.getFrame()
        self.height, self.width, _ = frame.shape

        # Create the location "quad" for simplicity
        print("Boundaries", self.parameters["location"])
        p1, p2      = self.parameters["location"]
        self.quad   = np.float32([[p1[0], p1[1]], [p2[0], p1[1]], [p2[0], p2[1]], [p1[0], p2[1]]])

        print("aft: ", self.quad)

    def run(self):
        if len(self.errors): return False

        # printf("Testing if ", self.parameters["objectID"], " is at location ", self.parameters["location"])

        tracked = self.vision.searchTrackedHistory(trackable=self.trackable)



        # If the object was not seen, exit
        if tracked is None: return False

        # print("Center: ", tracked.center, "Quad", tracked.quad)


        inCount = 0
        for coord in tracked.quad:
            if rv.pointInPolygon(coord, self.quad):
                inCount += 1




        # Check if the appropriate part of the object is within the boundaries
        ret = False
        if self.parameters["part"] == "any":
            ret =  inCount > 0

        if self.parameters["part"] == "all":
            ret =  inCount == 4

        if self.parameters["part"] == "center":
            center = sum(tracked.quad) / 4
            ret =  rv.pointInPolygon(center, self.quad)


        printf("Tested ", self.parameters["objectID"], " location. ", inCount, " points were the location:", ret)

        if self.parameters['not']: ret = not ret

        # If 'not', flip the return value
        return ret




#   LOGIC COMMANDS
class StartBlockCommand(Command):
    """
    Mark the start a block of code with this command
    """

    def __init__(self, env, interpreter, parameters=None):
        super(StartBlockCommand, self).__init__(parameters)


class EndBlockCommand(Command):
    """
    Mark the end a block of code with this command
    """

    def __init__(self, env, interpreter, parameters=None):
        super(EndBlockCommand, self).__init__(parameters)


class ElseCommand(Command):
    """
    Mark the end a block of code with this command
    """

    def __init__(self, env, interpreter, parameters=None):
        super(ElseCommand, self).__init__(parameters)


class SetVariableCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(SetVariableCommand, self).__init__(parameters)

        self.interpreter = interpreter

    def run(self):
        printf("Setting ", self.parameters["variable"], " to ", self.parameters["expression"])
        success = self.interpreter.setVariable(self.parameters["variable"],
                                               self.parameters["expression"])
        return success


class TestVariableCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(TestVariableCommand, self).__init__(parameters)
        self.interpreter = interpreter

    def run(self):
        interpreter   = self.interpreter

        # Get the variable. If that doesn't work, quit
        variableValue, successVar = interpreter.getVariable(self.parameters['variable'])
        if not successVar: return False


        # Evaluate the expression. If that doesn't work, quit
        compareValue, successExp = interpreter.evaluateExpression(self.parameters['expression'])
        if not successExp: return False

        # Compare the value of the expression using the operator from the parameters
        operations = ['==', '!=', '>', '<']
        expressionString = self.parameters['variable'] + operations[self.parameters['test']] + self.parameters["expression"]
        testResult, success = interpreter.evaluateExpression(expressionString)

        printf("Testing if ", self.parameters['variable'],
                                                         operations[self.parameters['test']],
                                                         self.parameters["expression"])

        # If the expression was evaluated correctly, then return the testResult. Otherwise, return False
        return testResult and success


class ScriptCommand(Command):

    def __init__(self, env, interpreter, parameters=None):
        super(ScriptCommand, self).__init__(parameters)

        # Load any objects, modules, calibrations, etc  that will be used in the run Section here. Use getVerifyXXXX()
        self.interpreter = interpreter
        self.env = env
        if len(self.errors): return

        # Here, start tracking if your command requires it
        # Add any objects to be tracked

    def run(self):
        if len(self.errors): return
        # printf("Running a custom script by user...")

        return self.interpreter.evaluateScript(self.parameters["script"])
