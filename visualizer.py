from direct.showbase.ShowBase import ShowBase
from panda3d.core import Light, Spotlight
from panda3d.core import PerspectiveLens
from panda3d.core import WindowProperties, MouseButton
from direct.task import Task
from math import pi, sin, cos
import pickle

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.blocks = []
        self.lastBlock = None
        self.firstBlock = True
        
        # self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.setUpControls()
        self.setUpCamera()
        self.loadBlockQueue()

        self.taskMgr.add(self.controllTask, 'ControllTask')
        self.taskMgr.doMethodLater(self.replaySpeed, self.queueTask, 'QueueTask')
        # self.taskMgr.add(self.queueTask), 'QueueTask'

    def addBlock(self, position, color=(0, 255, 0), state=0, solid=False):
        
        model = self.loader.loadModel('box')
        if solid:
            model.setTexture(self.loader.loadTexture('solid_box.png'))
        else:
            model.setTexture(self.loader.loadTexture('box.png'))
        model.setScale(1)
        model.setColor(*color)
        model.reparentTo(self.render)
        model.setTransparency(True)
        model.setPos(*position)
        self.blocks.append(model)

        if self.firstBlock :
            self.camera.setPos(*position)
            self.firstBlock = False

        return [model, state]

    def resetCamera(self):
        self.camera.reparentTo(self.render)
        self.camera.setPos(0, -20, 0)
        self.camera.setHpr(0, 0, 0)
        self.rotateX = 0
        self.rotateY = 0

    def setKey(self, key, val) :
        self.keys[key] = val

    def changeSpeed(self, delta):
        self.replaySpeed *= delta

    def setUpControls(self):
        self.keys = {'fwd' : 0, 'bwd' : 0, 'lft' : 0, 'rt' : 0, 'up' : 0, 'down' : 0, 'spdup' : 0, 'spddown' : 0}
        self.replaySpeed = 5
        self.accept('r', self.resetCamera)

        self.accept('w', self.setKey, ['fwd', 1])
        self.accept('w-up', self.setKey, ['fwd', 0])
        self.accept('s', self.setKey, ['bwd', 1])
        self.accept('s-up', self.setKey, ['bwd', 0])
        self.accept('d', self.setKey, ['rt', 1])
        self.accept('d-up', self.setKey, ['rt', 0])
        self.accept('a', self.setKey, ['lft', 1])
        self.accept('a-up', self.setKey, ['lft', 0])
        self.accept('z', self.setKey, ['up', 1])
        self.accept('z-up', self.setKey, ['up', 0])
        self.accept('x', self.setKey, ['down', 1])
        self.accept('x-up', self.setKey, ['down', 0])
        self.accept('p', self.setKey, ['spdup', 1])
        self.accept('p-up', self.setKey, ['spdup', 0])
        self.accept('o', self.setKey, ['spddown', 1])
        self.accept('o-up', self.setKey, ['spddown', 0])

        self.fwdStep = 0.5
        self.bwdStep = 0.5
        self.lftStep = 0.5
        self.rtStep = 0.5
        self.upStep = 0.3
        self.downStep = 0.3

        self.setUpMouse()

    def setUpMouse(self) :
        self.disableMouse()
        self.mouseMagnitude = 10
        self.rotateX, self.rotateY, self.rotateXd, self.rotateYd = 0, 0, 0, 0
        self.lastMouseX, self.lastMouseY = None, None

        self.taskMgr.add(self.mouseTask, "Mouse Task")
        self.scrolling = False

    def setUpCamera(self):
        self.resetCamera()

    def loadBlockQueue(self, path='queue.log'):
        with open(path, 'rb') as f:
            logs = pickle.load(f)
            self.blockQueue = logs[0]

    # def loadWorld(self):
    #     with open('world.data', 'rb') as f:
    #         self.world = pickle.load(f)
        
    #     for c_x in self.world.keys():
    #         for c_z in self.world[c_x].keys():


    def mouseTask (self, task):
        mw = base.mouseWatcherNode
        wp = WindowProperties()

        hasMouse = mw.hasMouse() 
        if hasMouse and mw.is_button_down(MouseButton.one()):
            x, y = mw.getMouseX(), mw.getMouseY()
            
            if not self.scrolling :
                    self.lastMouseX, self.lastMouseY = x, y
                    self.scrolling = True
            
            if self.lastMouseX is not None:
                
                dx, dy = x - self.lastMouseX, y - self.lastMouseY

            else:
                dx, dy = 0, 0

            self.lastMouseX, self.lastMouseY = x, y
            
        else:
            x, y, dx, dy, self.lastMouseX, self.lastMouseY = 0, 0, 0, 0, 0, 0
            self.scrolling = False
        
        if self.scrolling :
            self.rotateX += dx * 10 * self.mouseMagnitude
            self.rotateY -= dy * 10 * self.mouseMagnitude

            self.camera.setH(self.rotateX)
            self.camera.setP(self.rotateY)

        return Task.cont
        
    def controllTask(self, task):

        if self.keys['fwd'] == 1:
            self.camera.setY(self.camera, self.fwdStep)
        if self.keys['bwd'] == 1:
            self.camera.setY(self.camera, -self.bwdStep)
        if self.keys['lft'] == 1:
            self.camera.setX(self.camera, -self.lftStep)
        if self.keys['rt'] == 1:
            self.camera.setX(self.camera, self.rtStep)
        if self.keys['up'] == 1:
            self.camera.setZ(self.camera, self.upStep)
        if self.keys['down'] == 1:
            self.camera.setZ(self.camera, -self.downStep)
        if self.keys['spdup'] == 1:
            self.replaySpeed *= 1.2
        if self.keys['spddown'] == 1:
            self.replaySpeed *= 0.8

 
        return Task.cont

    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 0)
        self.camera.setHpr(angleDegrees, 0, 0)
        print(f"{self.camera.getPos()} {self.camera.getHpr()}")
        return Task.cont
    
    def queueTask(self, task):
        task.delayTime = 1 / self.replaySpeed
        block, state = self.blockQueue.pop(0)
        if state == -1:
            for model in self.blocks:
                model.setAlphaScale(0.1)
            for step in block[0]:
                print(step[0])
                self.addBlock([step[0][0], step[0][2], step[0][1]], solid=True)
            return
        block = (block[0], block[2], block[1])
        
        if self.lastBlock is not None:
            if self.lastBlock[1] == 0:
                self.lastBlock[0].setColor(255, 255, 0)
            elif self.lastBlock[1] == 1:
                self.lastBlock[0].setColor(255, 0, 0)
            elif self.lastBlock[1] == 2:
                self.lastBlock[0].setColor(0, 0, 0)


        self.lastBlock = self.addBlock(block, state=state)
        if state == 3:
            self.lastBlock[0].setColor(0, 0, 255)
        
        if self.blockQueue:
            return Task.again


 
app = MyApp()
app.run()