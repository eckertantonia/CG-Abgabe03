"""
/*******************************************************************************
 *
 *            #, #,         CCCCCC  VV    VV MM      MM RRRRRRR
 *           %  %(  #%%#   CC    CC VV    VV MMM    MMM RR    RR
 *           %    %## #    CC        V    V  MM M  M MM RR    RR
 *            ,%      %    CC        VV  VV  MM  MM  MM RRRRRR
 *            (%      %,   CC    CC   VVVV   MM      MM RR   RR
 *              #%    %*    CCCCCC     VV    MM      MM RR    RR
 *             .%    %/
 *                (%.      Computer Vision & Mixed Reality Group
 *
 ******************************************************************************/
/**          @copyright:   Hochschule RheinMain,
 *                         University of Applied Sciences
 *              @author:   Prof. Dr. Ulrich Schwanecke
 *             @version:   0.9
 *                @date:   23.05.2020
 ******************************************************************************/
/**         bezierTemplate.py
 *
 *          Simple Python OpenGL program that uses PyOpenGL + GLFW to get an
 *          OpenGL 3.2 context and display a Bezier curve.
 ****
"""
# Template s.o.
# bearbeitet von Antonia Eckert (Matr.-Nr.:1175268)

import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np

pointlist = []
index = 0
pointFound = False
yEnd = 0


class Scene:
    """ OpenGL 2D scene class """

    # initialization
    def __init__(self, width, height,
                 scenetitle="Bezier Curve Template"):
        self.scenetitle = scenetitle
        self.pointsize = 7
        self.linewidth = 5
        self.width = width
        self.height = height
        self.points = []
        self.lines = []
        self.points_on_bezier_curve = []
        self.kOrdnung = 3
        self.m = 3
        self.weights = []

    # set scene dependent OpenGL states
    def setOpenGLStates(self):
        glPointSize(self.pointsize)
        glLineWidth(self.linewidth)
        glEnable(GL_POINT_SMOOTH)

    # render
    def render(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # set foreground color to black
        glColor(0.0, 0.0, 0.0)

        # render all points
        glBegin(GL_POINTS)
        for p in self.points:
            glVertex2fv(p[:2])
        glEnd()

        if len(self.points) >= 2:
            # render polygon
            glLineWidth(self.linewidth)
            glBegin(GL_LINE_STRIP)
            for p in self.points:
                glVertex2f(p[0], p[1])
            glEnd()

            # render bezier curve
            glBegin(GL_LINE_STRIP)
            for p in self.points_on_bezier_curve:
                p[0] /= p[2]
                p[1] /= p[2]
                glVertex2f(p[0], p[1])
            glEnd()

            # set polygon
        self.determine_points_on_bezier_curve()

    def add_point(self, point):
        self.points.append(point)
        self.weights.append(1)  # Punkte und Gewicht haben gleichen Index
        if len(self.points) >= self.m:
            if self.m >= self.kOrdnung:
                self.determine_points_on_bezier_curve()
            else:
                print("m kleiner k")

    # clear polygon
    def clear(self):
        self.points = []
        self.weights = []
        self.points_on_bezier_curve = []

    # determine line code
    def determine_points_on_bezier_curve(self):
        self.points_on_bezier_curve = []

        grad = self.kOrdnung
        knotvector = []
        knotvector.extend([0 for i in range(grad)])
        last = len(self.points) - 1 - (grad - 2)
        knotvector.extend([x for x in range(1, last)])
        knotvector.extend([last for x in range(grad)])

        t = 0  # von m abhaengig
        while t < knotvector[-1]:
            r = self.findR(knotvector, t)
            p = self.deBoor(self.points, knotvector, t, grad - 1, r)
            t += 1 / float(self.m)
            self.points_on_bezier_curve.append(p)

    def deBoor(self, controlpoints, knotvector, t, rek, r):
        if rek == 0:
            return controlpoints[r] * np.array(self.weights[r])

        alpha = (t - knotvector[r]) / (knotvector[r - rek + self.kOrdnung] - knotvector[r])
        newPoint = ((1 - alpha) * np.array(self.deBoor(controlpoints, knotvector, t, rek - 1, r - 1))
                    + alpha * np.array(self.deBoor(controlpoints, knotvector, t, rek - 1, r)))

        return newPoint

    ## erster deBoor-Versuch. funktioniert leider nicht mit Gewichtung der Punkte
    #
    # def deboor(self, grad, controlpoints, knotvector, t):
    #     r = self.findR(knotvector, t)
    #
    ##     for i in range(len(controlpoints)):
    ##         controlpoints[i][0] *= self.weights[i]
    ##         controlpoints[i][1] *= self.weights[i]
    ##         controlpoints[i][2] *= self.weights[i]
    ##     pointInterval = controlpoints[r - grad + 1: r + 1]  # passender ausschnitt aus controlpoints
    #
    #     if len(pointInterval) > 0:
    #         return self.rek(grad, pointInterval, knotvector, t, r)
    #     else:
    #         return controlpoints
    #
    # def rek(self, grad, controlpoints, knotvector, t, r):
    #     if len(controlpoints) <= 1:
    #         return controlpoints[0]
    #
    #     newPoints = []
    #     knotInterval = [knotvector[i] for i in range(r - grad + 1, r + grad + 1)]
    #     controlnps = np.array(controlpoints) # damit werte im array multipliziert werden koennen
    #
    #     for i in range(len(controlpoints) - 1):
    #         sKnotInterval = knotInterval[i:i + grad + 1]
    #         fac = (t - sKnotInterval[0]) / (sKnotInterval[-1] - sKnotInterval[0])  # distanzfaktor
    #         newPoint = controlnps[i] * (1 - fac) + controlnps[i + 1] * fac
    #         newPoints.append(newPoint)
    #
    #     return self.rek(grad - 1, newPoints, knotvector, t, r)

    def findR(self, knotvector, t):
        for i in range(len(knotvector)):
            if knotvector[i] > t:
                return i - 1  # wenn Wert in Knotenvektor an pos i groeser, dann r = i-1


class RenderWindow:
    """GLFW Rendering window class"""

    def __init__(self, scene):

        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 100

        # make a window
        self.width, self.height = scene.width, scene.height
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, scene.scenetitle, None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -2, 2)
        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)
        glfw.set_cursor_pos_callback(self.window, self.onMouseMotion)

        # create scene
        self.scene = scene  # Scene(self.width, self.height)
        self.scene.setOpenGLStates()

        # exit flag
        self.exitNow = False

    def onMouseButton(self, win, button, action, mods):
        global index, pointFound, yEnd
        print("mouse button: ", win, button, action, mods)

        if action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(win)

            if mods == glfw.MOD_SHIFT:
                for i in range(len(self.scene.points)):
                    if y - 10 < self.scene.points[i][1] < y + 10:
                        index = i
                        pointFound = True
                        yEnd = y
            else:
                p = [int(x), int(y), 1]
                scene.add_point(p)

        if action == glfw.RELEASE:
            pointFound = False

    def onMouseMotion(self, win, x, y):
        global pointFound, index, yEnd
        if pointFound:
            diffY = yEnd - y
            if diffY > 0:
                if self.scene.weights[index] < 10:
                    self.scene.weights[index] += 1
            elif diffY < 0:
                if self.scene.weights[index] > 1:
                    self.scene.weights[index] -= 1

    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            # clear everything
            if key == glfw.KEY_C:
                self.scene.clear()

            # Ordnung aendern
            if mods == glfw.MOD_SHIFT:
                if key == glfw.KEY_K:
                    if self.scene.kOrdnung < len(self.scene.points):
                        self.scene.kOrdnung += 1
                if key == glfw.KEY_M:
                    self.scene.m += 1
            else:
                if key == glfw.KEY_K:
                    if self.scene.kOrdnung > 3:
                        self.scene.kOrdnung -= 1
                if key == glfw.KEY_M:
                    if self.scene.m > 1:
                        self.scene.m -= 1

            if self.scene.kOrdnung > self.scene.m:
                print("k > m")
            else:
                self.scene.determine_points_on_bezier_curve()

    def onSize(self, win, width, height):
        print("onsize: ", win, width, height)
        self.width = width
        self.height = height
        self.aspect = width / float(height)
        glViewport(0, 0, self.width, self.height)

    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0 / self.frame_rate:
                # update time
                t = currT
                # clear viewport
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                # render scene
                self.scene.render()
                # swap front and back buffer
                glfw.swap_buffers(self.window)
                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()


# call main
if __name__ == '__main__':
    print("bezierTemplate.py")
    print("pressing 'C' should clear the everything")

    # set size of render viewport
    width, height = 640, 480

    # instantiate a scene
    scene = Scene(width, height, "Bezier Curve with deBoor-Algorithm - Eckert")

    rw = RenderWindow(scene)
    rw.run()
