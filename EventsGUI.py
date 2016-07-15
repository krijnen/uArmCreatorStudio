from PyQt5        import QtGui, QtCore, QtWidgets
from Logic        import Paths
from Logic.Global import printf


class EventWidget(QtWidgets.QWidget):
    """
    This is the widget that appears on the EventList.
    It's supposed to be prettier than the normal list items.
    """
    def __init__(self, parent):
        super(EventWidget, self).__init__(parent)
        self.title        = QtWidgets.QLabel()
        self.primaryIcon  = QtWidgets.QLabel("No icon found.")
        self.optionalIcon = QtWidgets.QLabel("")

        self.optionalIcon.hide()
        self.initUI()


    def initUI(self):
        font = QtGui.QFont()
        font.setBold(True)
        self.title.setFont(font)

        mainHLayout = QtWidgets.QHBoxLayout()
        mainHLayout.addWidget(self.primaryIcon)
        mainHLayout.addWidget(self.optionalIcon)
        mainHLayout.addWidget(self.title, QtCore.Qt.AlignLeft)

        self.setLayout(mainHLayout)

    def setTitle(self, text):
        self.title.setText(text)

    def setIcon(self, icon):
        self.primaryIcon.setPixmap(QtGui.QPixmap(icon))


    def setTip(self, tip):
        self.setToolTip(tip)


class EventPromptWindow(QtWidgets.QDialog):
    def __init__(self, objectManager, parent):
        super(EventPromptWindow, self).__init__(parent)


        self.objManager       = objectManager  # Used to generate the "recognize object" event

        self.accepted         = False
        self.chosenEvent      = None  #What event the user chose to add (changed in btnClicked() function)
        self.chosenParameters = None  # Any extra parameters about the event (AKA,type of object, key, number, or motion

        # UI Stuff
        self.buttonWidth = 150
        self.initUI()               # Actually format and place everything

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # TODO: Investigate adding this to command windows
        self.exec_()  #Open self, and prevent anyone clicking on other windows


    def initUI(self):
        self.initButtons()          # Create the event "Buttons"

        ####   Actually format and place everything   #####
        # Create grid layout
        grid = QtWidgets.QGridLayout()

        # Left column
        grid.addWidget(      self.initBtn, 0, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(      self.stepBtn, 1, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(   self.destroyBtn, 2, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(       self.tipBtn, 3, 0, QtCore.Qt.AlignLeft)

        # Right column
        grid.addWidget(  self.keyboardBtn, 0, 1, QtCore.Qt.AlignLeft)
        grid.addWidget(    self.motionBtn, 1, 1, QtCore.Qt.AlignLeft)
        grid.addWidget(      self.seenBtn, 2, 1, QtCore.Qt.AlignLeft)
        grid.addWidget(   self.notSeenBtn, 3, 1, QtCore.Qt.AlignLeft)

        # Set up Cancel button in it's own layout:
        cancelLayout = QtWidgets.QHBoxLayout()
        cancelLayout.addWidget(self.cancelBtn)


        # Create main layout
        mainVLayout = QtWidgets.QVBoxLayout()
        mainVLayout.addLayout(grid)
        mainVLayout.addLayout(cancelLayout, QtCore.Qt.AlignHCenter)


        # Finalize everything
        self.setLayout(mainVLayout)
        self.setFixedSize(self.sizeHint())  #Make the window a fixed size
        self.setWindowTitle('Add an Event')

    def initButtons(self):

        # Create the cancel button
        self.cancelBtn    = QtWidgets.QPushButton('Cancel')
        self.cancelBtn    .setFixedWidth(self.buttonWidth * 1.5)
        self.cancelBtn    .setFixedHeight(25)
        # self.cancelBtn    .setIcon(QtGui.QIcon(Icons.cancel))  # With this there, I feel like I'm copying game maker


        # Create Event Buttons
        self.initBtn      = self.getNewButton( 'Initialization',         InitEventGUI.icon)
        self.destroyBtn   = self.getNewButton( 'End of Program',      DestroyEventGUI.icon)
        self.stepBtn      = self.getNewButton(           'Step',         StepEventGUI.icon)
        self.tipBtn       = self.getNewButton(     'Tip Sensor',          TipEventGUI.icon)
        self.keyboardBtn  = self.getNewButton(       'Keyboard',     KeypressEventGUI.icon)
        self.motionBtn    = self.getNewButton(         'Motion',       MotionEventGUI.icon)
        self.seenBtn      = self.getNewButton(     'Recognized', RecognizeObjectEventGUI.icon)
        self.notSeenBtn   = self.getNewButton( 'Not Recognized', Paths.event_not_recognize)


        # CONNECT BUTTONS THAT DON'T HAVE MENUS
        self.initBtn.clicked.connect(lambda: self.btnClicked(   InitEventGUI))
        self.destroyBtn.clicked.connect(lambda: self.btnClicked(DestroyEventGUI))
        self.stepBtn.clicked.connect(lambda: self.btnClicked(   StepEventGUI))
        self.tipBtn.clicked.connect(lambda: self.btnClicked(    TipEventGUI))
        self.motionBtn.clicked.connect(lambda: self.btnClicked( MotionEventGUI))
        self.cancelBtn.clicked.connect(self.cancelClicked)


        # Initialize the menus for the rest of the buttons
        self.initButtonMenus()      # Populate any event buttons that have drop down menus

    def initButtonMenus(self):
        """
        initBtn         NO menu
        keyboardBtn     Has menu
        stepBtn         Has menu
        intersectBtn    Has menu
        cancelBtn       NO menu
        :return:
        """
        # Set up Menus for buttons that have menus:

        ######################     KEYBOARD MENU     ######################
        keyboardMnu = QtWidgets.QMenu()

        # Create Letters Sub Menu
        self.lettersSubMnu = QtWidgets.QMenu("Letters") # Has to be self or something glitches with garbage collection.
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','J', 'K', 'L', 'M',
                    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        for letter in alphabet:
            # About the lambda letter=letter:. I don't know why it fixes the problem, but it does. Here's a better
            # Explanation: http://stackoverflow.com/questions/4578861/connecting-slots-and-signals-in-pyqt4-in-a-loop
            self.lettersSubMnu.addAction(letter, lambda letter=letter: self.btnClicked(KeypressEventGUI, params={"checkKey": letter}))

        # Create Digits Sub Menu
        self.digitsSubMnu = QtWidgets.QMenu("Digits")
        digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for index, digit in enumerate(digits):
            self.digitsSubMnu.addAction(digit, lambda digit=digit: self.btnClicked(KeypressEventGUI, params={"checkKey": digit}))

        # Add Sub Menus
        keyboardMnu.addMenu(self.lettersSubMnu)
        keyboardMnu.addMenu(self.digitsSubMnu)
        self.keyboardBtn.setMenu(keyboardMnu)


        ######################     MOTION MENU     ######################
        newMotionBtn = lambda params: self.btnClicked(MotionEventGUI, params=params)
        motionMnu    = QtWidgets.QMenu()

        motionMnu.addAction("Above 'Low' Speed", lambda: newMotionBtn({"low":  "Low", "high":  "Inf"}))
        motionMnu.addAction("Above 'High' Speed", lambda: newMotionBtn({"low": "High", "high":  "Inf"}))
        motionMnu.addSeparator()
        motionMnu.addAction("Less than 'Low' Speed", lambda: newMotionBtn({"low": "None", "high":  "Low"}))
        motionMnu.addAction("Less than 'High' Speed", lambda: newMotionBtn({"low": "None", "high": "High"}))
        motionMnu.addSeparator()
        motionMnu.addAction("Between 'Low' to 'High' Speed", lambda: newMotionBtn({"low":  "Low", "high": "High"}))


        self.motionBtn.setMenu(motionMnu)



        trackableList   = self.objManager.getObjectNameList(objFilter=self.objManager.TRACKABLE)
        ######################   RECOGNIZE/NOT MENUS    ######################

        newRecognizeBtn = lambda params: self.btnClicked(    RecognizeObjectEventGUI, params=params)
        newCascadeBtn   = lambda params: self.btnClicked(RecognizeCascadeEventGUI, params=params)
        recMnu          = QtWidgets.QMenu()
        notRecMnu       = QtWidgets.QMenu()

        # Add cascade tracking options
        recMnu.addAction(        "Face Detected", lambda: newCascadeBtn({'objectID':  "Face", "not": False}))
        notRecMnu.addAction( "Face Not Detected", lambda: newCascadeBtn({'objectID':  "Face", "not":  True}))
        recMnu.addAction(       "Smile Detected", lambda: newCascadeBtn({'objectID': "Smile", "not": False}))
        notRecMnu.addAction("Smile Not Detected", lambda: newCascadeBtn({'objectID': "Smile", "not":  True}))

        recMnu.addSeparator()
        notRecMnu.addSeparator()

        # Add the objects for the recognized menu and the "not" recognized menu
        for name in trackableList:
            recMnu.addAction(   name, lambda name=name: newRecognizeBtn({'objectID': name, "not": False}))
            notRecMnu.addAction(name, lambda name=name: newRecognizeBtn({'objectID': name, "not":  True}))

        self.seenBtn.setMenu(recMnu)
        self.notSeenBtn.setMenu(notRecMnu)



    def btnClicked(self, eventType, **kwargs):
        printf("Event Type ", eventType, "selected")
        self.chosenEvent      = eventType
        self.chosenParameters = kwargs.get("params", None)
        self.accepted = True
        self.close()

    def cancelClicked(self, event):
        self.close()


    def getNewButton(self, buttonText, icon):

        newButton = QtWidgets.QPushButton(buttonText)
        newButton.setStyleSheet("Text-align:left")
        newButton.setFixedWidth(self.buttonWidth)
        newButton.setIcon(QtGui.QIcon(icon))
        return newButton


class EventGUI:
    # Priority determines how the events will be sorted. 0 means the event will be at the top. 10000 is last.
    priority = 5000
    title = ""

    def __init__(self, parameters):
        """
        self.parameters is used for events like KeyPressEvent where one class can handle multiple types of events
        such as A KeyPress or ZKeypress. THe self.parameters makes sure that you can differentiate between events
        when adding new ones, so you can make sure there aren't two 'A Keypress' events.
        """
        self.parameters  = parameters  # Parameters will be none for some events, but its important to save them
        if self.parameters is None:
            self.parameters = {}
        self.commandList = None

    def dressWidget(self, widget):
        widget.setIcon(self.icon)
        widget.setTitle(self.title)
        widget.setTip(self.tooltip)
        return widget



########## EVENTS ##########
"""
EXAMPLE CLASS

class NameEventGUI(EventGUI):
    icon      = Icons.name_event
    logicPair = 'NameEvent'

    title     = "Some title"  # Unless it's a parameter event, then title and tooltip are set in self.dressWidget
    tooltip   = "Some tooltip explanation"

    def __init__(self, parameters):
        super(NameEventGUI, self).__init__(parameters)


    def dressWidget(self, widget):
        # Format the widget that will show up to make it unique. Not necessary in non-parameter events
        widget.setIcon(self.icon)
        widget.setTitle('Name ' + self.parameters["someparameter"])
        widget.setTip('Activates when the some condition ' + self.parameters["someparameter"] + " is pressed")
        return widget

"""
#   SIMPLE, NO-PARAMETER EVENTS
class InitEventGUI(EventGUI):
    title     = 'Initialization'
    tooltip   = 'Activates once each time the program is run'
    icon      = Paths.event_creation
    logicPair = 'InitEvent'
    priority  = 0

    def __init__(self, parameters):
        super(InitEventGUI, self).__init__(parameters)


class DestroyEventGUI(EventGUI):
    title     = 'End of Program'
    tooltip   = 'Activates once, when the program is ended'
    icon      = Paths.event_destroy
    logicPair = 'DestroyEvent'
    priority  = 10000

    def __init__(self, parameters):
        super(DestroyEventGUI, self).__init__(parameters)


class StepEventGUI(EventGUI):
    title     = 'Step'
    tooltip   = 'Activates every time the events are refreshed'
    icon      = Paths.event_step
    logicPair = 'StepEvent'
    priority  = 100

    def __init__(self, parameters):
        super(StepEventGUI, self).__init__(parameters)


class TipEventGUI(EventGUI):
    """
    This event activates when the sensor on the tip of the robots sucker is pressed/triggered
    """

    title     = 'Tip Pressed'
    tooltip   = 'Activates when the sensor on the tip of the arm is pressed'
    icon      = Paths.event_tip
    logicPair = 'TipEvent'
    priority  = 200

    def __init__(self, parameters):
        super(TipEventGUI, self).__init__(parameters)




#   EVENTS WITH PARAMETERS
class KeypressEventGUI(EventGUI):
    title     = "Key Pressed"
    icon      = Paths.event_keyboard
    logicPair = 'KeypressEvent'
    priority  = 300

    def __init__(self, parameters):
        super(KeypressEventGUI, self).__init__(parameters)

    def dressWidget(self, widget):
        self.title = 'KeyPress ' + self.parameters["checkKey"]
        widget.setIcon(self.icon)
        widget.setTitle('Keypress ' + self.parameters["checkKey"])
        widget.setTip('Activates when the letter ' + self.parameters["checkKey"] + " is pressed")
        return widget


class MotionEventGUI(EventGUI):
    """
    This event activates when the sensor on the tip of the robots sucker is pressed/triggered
    """
    title     = "Motion Detected"
    icon      = Paths.event_motion
    logicPair = 'MotionEvent'
    priority  = 400

    def __init__(self, parameters):
        super(MotionEventGUI, self).__init__(parameters)

        title = ""
        if self.parameters["high"] == "Inf":
            title = "Above " + self.parameters["low"] + " Speed"
        elif self.parameters["low"] == "None":
            title = "Less Then " + self.parameters["high"] + " Speed"
        elif self.parameters["low"] == "Low":
            title = "Low to High Speed"

        self.title = title

    def dressWidget(self, widget):

        widget.setIcon(self.icon)
        widget.setTitle(self.title)  # 'Motion ' + self.parameters["low"] + "-" + self.parameters["high"])
        widget.setTip('Activates when there is motion detected')

        return widget


class RecognizeObjectEventGUI(EventGUI):
    title     = "Object Recognized"
    icon      = Paths.event_recognize   # Changes in self.dressWidget in this case
    logicPair = 'RecognizeObjectEvent'
    priority  = 500

    def __init__(self, parameters):
        super(RecognizeObjectEventGUI, self).__init__(parameters)

        if parameters["not"]: self.priority += 10

    def dressWidget(self, widget):
        self.title = "Object '" + self.parameters["objectID"] + "' Recognized"

        # Format the widget that will show up to make it unique. Not necessary in non-parameter events
        if self.parameters["not"]:
            widget.setIcon(Paths.event_not_recognize)
        else:
            widget.setIcon(self.icon)

        widget.setTitle(self.parameters["objectID"].replace("_", " "))
        widget.setTip('Activates when the object ' + self.parameters["objectID"] + " is seen on camera.")
        return widget


class RecognizeCascadeEventGUI(RecognizeObjectEventGUI):
    title     = "Object Recognized"
    logicPair = "RecognizeCascadeEvent"

    def __init__(self, parameters):
        super(RecognizeCascadeEventGUI, self).__init__(parameters)



