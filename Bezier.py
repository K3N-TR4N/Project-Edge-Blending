import matplotlib.pyplot as plt

from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.backend_bases import MouseButton

def left_mouse_clicked(event):
    if event.button is MouseButton.LEFT:
        print('Mouse Clicked!')
        print('\nMouse X Data: ', event.xdata)
        print('Mouse Y Data: ', event.ydata)
        print('\nMouse X Coordinate: ', event.x)
        print('Mouse Y Coordinate: ', event.y)

def main():
    control_points_1 = [(0, 0), (0.5, 0.5), (0, 1)]
    control_points_2 = [(0, 1), (0.5, 0), (1, 1)]
    control_points_3 = [(1, 0), (0.5, 0.5), (1, 1)]

    figure, axes = plt.subplots()
    bezier_curve_1 = PathPatch(Path(control_points_1, [Path.MOVETO, Path.CURVE3, Path.CURVE3]))
    bezier_curve_2 = PathPatch(Path(control_points_2, [Path.MOVETO, Path.CURVE3, Path.CURVE3]))
    bezier_curve_3 = PathPatch(Path(control_points_3, [Path.MOVETO, Path.CURVE3, Path.CURVE3]))

    axes.add_patch(bezier_curve_1)
    axes.add_patch(bezier_curve_3)
    axes.add_patch(bezier_curve_2)

    plt.connect('button_press_event', left_mouse_clicked)
    plt.show()

main()
