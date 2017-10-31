import hologui as hg
import holopy as hp
import numpy as np
import sys
import qimage2ndarray as qim
from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets
from scipy.ndimage.measurements import center_of_mass
import os
from scipy.misc import fromimage
from PIL import Image as pilimage
from picprocessing import create_temp_pictures
from matplotlib import pyplot
import call_fiji


def load_back_image(window):
    print("load_back_image called")
    global back
    try:
        back = create_temp_files(1)
    except:
        return
    scene = QtWidgets.QGraphicsScene() #scene: manipulate data to be shown in widget
    image = qim.array2qimage(back.values[0]) #get x-y values of the image and convert to QImage
    scene.addPixmap(QtGui.QPixmap(image).scaledToWidth(ui.GraphicsViewBackground.width()-2)) #QImage->QPixmap and add to the scene
    ui.GraphicsViewBackground.setScene(scene) #set the scene to the background widget
    ui.GraphicsViewBackground.show() #show the picture
    

def load_sample():
    print("load_sample called.")
    global raw
    try:
        raw = create_temp_files(0)
    except:
        return
    scene = QtWidgets.QGraphicsScene()  # scene: manipulate data to be shown in widget
    image = qim.array2qimage(raw.values[0])  # get x-y values of the image and convert to QImage
    scene.addPixmap(QtGui.QPixmap(image).scaledToWidth(ui.GraphicsViewSample.width()-2))  # QImage->QPixmap and add to the scene
    ui.GraphicsViewSample.setScene(scene)  # set the scene to the background widget
    ui.GraphicsViewSample.show()  # show the picture

def save_holos():
    print("save_holos called.")
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog

    try:
        rec_vol
    except:
        print("rec_vol ist not defined!")
        return
    global dirName
    dirName, _ = QtWidgets.QFileDialog.getSaveFileName(None,"QFileDialog.getSaveFileName()","","Dir of Pic Files (*.png)", options=options)
    if dirName:
        try:
            os.stat(dirName)
        except:
            os.mkdir(dirName)
        print("Directorty {} create".format(dirName))
        for i in range(len(rec_vol)):
            image = qim.array2qimage(np.abs(rec_vol.values[i]), True)
            image.save(dirName + '/holo_' + str(i) + '.png')

def save_params():
    print("save_params called.")
    with open('params.ini', 'w') as f:
        f.write("{}\t{}\n".format(ui.LabelSpacing.text(), ui.SpinBoxSpacing.value()))
        f.write("{}\t{}\n".format(ui.LabelWavelength.text(), ui.SpinBoxWavelength.value()))
        f.write("{}\t{}\n".format(ui.LabelPolarization.text(), ui.SpinBoxMagnification.value()))
        f.write("{}\t{}\n".format(ui.LabelMedium.text(), ui.SpinBoxMedium.value()))
        f.write("{}\t{}\n".format(ui.LabelDistance.text(), ui.SpinBoxDistance.value()))
        f.write("{}\t{}\n".format(ui.LabelZMin.text(), ui.SpinBoxZMin.value()))
        f.write("{}\t{}\n".format(ui.LabelZMax.text(), ui.SpinBoxZMax.value()))
        f.write("{}\t{}\n".format(ui.LabelZSteps.text(), ui.SpinBoxZStep.value()))
        f.write("{}\t{}\n".format(ui.LabelZNPixOut.text(), ui.SpinBoxNPixOut.value()))
    f.close()



def load_params():
    print("load_params called.")
    return
    #with open('params.ini', 'r') as f:
        #print(f.readall())
    #f.close()

def show_about():
    print("show_about called.")
    pass

def app_quit():
    print("app_quit called.")
    exit()

def save_averaged_back():
    print("save_averaged_back called.")
    try:
        image = qim.array2qimage(np.abs(back.values[0]), True)
        image.save("average_background.png")
    except:
        print("No background image saved.")

def load_dark_field():
    #global dark_field
    #print("load_dark_field called")
    #dark_field = create_temp_files(0)
    try:
        rec_vol
    except:
        return
    scene = QtWidgets.QGraphicsScene()  # scene: manipulate data to be shown in widget
    image = qim.array2qimage(np.abs(rec_vol.values[ui.HorizontalSliderHologram.value()]), True)  # get x-y values of the image and convert to QImage
    scene.addPixmap(QtGui.QPixmap(image).scaledToWidth(ui.GraphicsViewDarkField.width()-2))  # QImage->QPixmap and add to the scene
    ui.GraphicsViewDarkField.setScene(scene)  # set the scene to the background widget                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ui.GraphicsViewDarkField.show()  # show the picture

def calculate_hologram(window):
    print("calculate_hologram called.")
    try:
        back
        raw
    except:
        print("calculate_hologram called with no data pls make sure background and hologram is available.")
        return
    global rec_vol

    if ui.TabSources.currentIndex() is 0:
        print("calculate_hologram called with point source!")

        #Calculate background correction and update metadata
        holo = hp.core.process.bg_correct(raw, back+1, back)
        holo = hp.core.update_metadata(holo, medium_index=window.SpinBoxMedium.value(), illum_wavelen=window.SpinBoxWavelength.value()*1e-9)

        #get beam center and set output shape
        beam_c = center_of_mass(back.values.squeeze())
        out_schema = hp.core.detector_grid(shape=ui.SpinBoxNPixOut.value(), spacing=ui.SpinBoxSpacing.value() * 1e-6 / ui.SpinBoxMagnification.value())
        zstack = np.linspace(window.SpinBoxZMin.value()*1e-6, window.SpinBoxZMax.value()*1e-6, num = window.SpinBoxZStep.value(), endpoint=True)

        #propagate through the raw hologram in zstack defined distances to reconstruct the wavefront at the object of interest
        rec_vol = hp.propagation.ps_propagate(holo, zstack, ui.SpinBoxDistance.value()*1e-3, beam_c, out_schema)
        #process the reconstructions
    else:
        print("calculate_hologram called with collimated source!")
        holo = hp.core.process.bg_correct(raw, back)
        holo = hp.core.update_metadata(holo, medium_index=window.SpinBoxMedium_2.value(), illum_wavelen=window.SpinBoxWavelength_2.value()*1e-9)

        zstack = np.linspace(window.SpinBoxZMin_2.value()*1e-6, window.SpinBoxZMax_2.value()*1e-6, num = window.SpinBoxZStep_2.value(), endpoint=True)

        rec_vol = hp.propagate(holo, zstack)
        #process the reconstruct further
    scene = QtWidgets.QGraphicsScene()  # scene: manipulate data to be shown in widget
    image = qim.array2qimage(np.abs(rec_vol.values[0]), True)  # get x-y values of the image and convert to QImage
    scene.addPixmap(QtGui.QPixmap(image).scaledToWidth(ui.GraphicsViewHologram.width()-2))  # QImage->QPixmap and add to the scene
    ui.GraphicsViewHologram.setScene(scene)  # set the scene to the background widget
    ui.GraphicsViewHologram.show()  # show the picture
    ui.HorizontalSliderHologram.setMaximum(ui.SpinBoxZStep.value()-1)
    ui.HorizontalSliderHologram.setEnabled(True)
    print("Done calculation.")

def slide_hologram():
    print("slide_hologram called.")
    #print(ui.HorizontalSliderHologram.value())
    scene = QtWidgets.QGraphicsScene()  # scene: manipulate data to be shown in widget
    image = qim.array2qimage(np.abs(rec_vol.values[ui.HorizontalSliderHologram.value()]), True)  # get x-y values of the image and convert to QImage
    scene.addPixmap(QtGui.QPixmap(image).scaledToWidth(ui.GraphicsViewHologram.width()-2))  # QImage->QPixmap and add to the scene
    ui.GraphicsViewHologram.setScene(scene)  # set the scene to the background widget
    ui.GraphicsViewHologram.show()
    #ui.HoloGramData.setText("Distance {} Z Stack {}".format(ui.HorizontalSliderHologram.value(), "1234"))

def create_temp_files(case):
    if case is 0:
        filename = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', '')
        if filename is "":
            return
        file = []
        file.append(filename[0])
        return hp.core.io.load_image(create_temp_pictures(file)[0], spacing=ui.SpinBoxSpacing.value()*1e-6)
    elif case is 1:
        filenames = QtWidgets.QFileDialog.getOpenFileNames(None, 'Open Files', '')
        if filenames is "":
            return
        return hp.core.io.load_average(create_temp_pictures(filenames[0]), spacing=ui.SpinBoxSpacing.value()*1e-6)

def call_FiJi_3D():
    try:
        dirName
        call_fiji.callFJ(dirName)
    except:
        return

if __name__ == "__main__":
    #GLOBALS
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = hg.Ui_MainWindow()
    ui.setupUi(MainWindow)
    #connect button to functions
    ui.PushButtonBackground.clicked.connect(partial(load_back_image, ui))
    ui.PushButtonSample.clicked.connect(partial(load_sample))
    ui.PushButtonHologram.clicked.connect(partial(calculate_hologram, ui))
    ui.PushButtonDarkField.clicked.connect(partial(load_dark_field))
    ui.HorizontalSliderHologram.valueChanged.connect(slide_hologram)
    ui.pushButton.clicked.connect(call_FiJi_3D)
    #connect Menu entries to functions
    ui.actionSave_Hologram_as.triggered.connect(partial(save_holos))
    ui.actionExit.triggered.connect(app_quit)
    ui.actionAbout.triggered.connect(show_about)
    ui.actionSave_Config.triggered.connect(save_params)
    ui.actionLoad_Config.triggered.connect(load_params)
    ui.actionSave_averaged_background.triggered.connect(save_averaged_back)
    #Enable the Hologram Button
    ui.PushButtonHologram.setEnabled(True)
    ui.SpinBoxMedium_2.setEnabled(True)
    ui.SpinBoxMedium_2.setMinimum(0)
    ui.SpinBoxMedium_2.setMaximum(10)
    MainWindow.show()
    sys.exit(app.exec_())

