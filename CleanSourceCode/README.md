# Planetarium Edge Blending
This project is a tool made for the University of Texas at Arlington's Planetarium staff to allow for edge blending programmatically through an easy-to-use interface that allows for custom masks to be made for different client projectors.
## Installation
There are two main programs used in this project, a graphical user interface for making masks intended for a host computer, as well as the client overlay that applies the mask on client computers.
### Host GUI
Locate the "Host GUI" folder. Choose a location on your **HOST** computer to copy this folder to (it can be anywhere). Within this folder there are two items, a folder called "data" that contains the files needed to run the program, and a shortcut to EdgeBlendingGUI.exe. You can ignore the data folder. The exe shortcut is used to run the program. For ease of access, you can right click it and "Pin To Start".
### Client Overlay
**The following must be done on each client you wish to use this program with:**
1. Locate the "Client Overlay" folder.
2. Choose a location on the given client computer to copy this folder to (it can be anywhere).
3. As with the Host GUI, ignore the data folder. The shortcut to EdgeBlendingClient.exe will be the only relevant file. Run the file to ensure it works.
4. (do the following when ready to use the software full-time) Right click on the EdgeBlendingClient.exe shortcut and click copy.
5. Press Windows Key + R at the same time to bring up the run dialog.
6. Type in shell:startup and hit OK.
7. Paste the file into the folder that opened. This will ensure that the client overlay application opens each time the client computer is restarted.
## Running the programs
For more information on how to run the programs, refer to the user manual.
## Source Code
Like the project itself, the source code is divided into two main categories: the Host GUI and the Client Overlay.
### Host GUI
One main python script is used to run the program. Additionally, for each screen of the program (of which there are 3), there is a corresponding UI file generated by PyQt5 Designer which is used to dictate the UI layout. There is also one text file used by the program, client_ip.txt, which must be present for the program to run.
### Client Overlay
One python script is used to display the overlay. Two files are generated by the program for use in the program: bezierinfo and figure.png. bezierinfo is a file containing the bezier information in bytes format, and figure.png is the corresponding mask used by the client overlay application.
## Making Changes
If any edits have been made in the source code, the executable used for the corresponding program must be regenerated. Our current implementation uses [PyInstaller](https://pyinstaller.org/en/stable/) which generates an executable and folders based on the libraries included in the python script. Refer to the PyInstaller documentation for more information.<br /><br />
**NOTE**<br />
If you make changes to the Host GUI, after generating the executable using PyInstaller, make sure to include the UI files as well as the client_ip.txt in the newly generated dist folder.
