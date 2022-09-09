This program is free software.
It is licensed under the GNU GPL version 3 or later.
That means you are free to use this program for any purpose;
free to study and modify this program to suit your needs;
and free to share this program or your modifications with anyone.
If you share this program or your modifications
you must grant the recipients the same freedoms.
To be more specific: you must share the source code under the same license.
For details see https://www.gnu.org/licenses/gpl-3.0.html

# GIScan
GIScan is a simple tool to open and analyze data stored in cbf (Crystallographic Binary Format) files. While
GIScan is primarily developed with the analyis of GISAXS data in mind, as obtained by the P03 beamline of PETRA
III at the DESY Synchrotron in Hamburg, Germany, it should be compatible with any arbitrary cbf data.

GIScan handles raw data directly and doesn't need any a-priori data reduction. It supports features such as
background subtraction, line scans along the Qy and Qz axis, detection of the full-width at half-maximum (FWHM)
of diffraction peaks and coordinate conversion from pixels to reciprocal or angular space
      
The region of interest (ROI) over which the scans are made can be moved by selecting the required position in the obtained in-plane or the out-of-plane scans. Alternatively a region can be selected by dragging the mouse over the GISAXS mapping, or entered manually using the coordinate positions in the bottom-left corner. Using the Background selection function, an ROI can be chosen for the background as well and the average background intensity will be substracted from the scans that are made. Both the vertical and the horizontal scan can be exported in plain .txt files for further analysis. 

GIScan is mostly developed with the analysis of multilayers in mind but can be used for any arbitrary data stored
in cbf format. If a beamline or datatype (be it GISAXS or GISANS) is not supported and you would like to use this
tool, please submit an issue on the Github page so this can be arranged.
      
For any support or other questions, please contact me at info@sjoerd.se. Keep in mind that this program comes with 
absolutely no warranty or formal support, but I will try my best to be of assistance.  

# How to install: 

**Windows:** An executable file can be found on the releases page on the right-hand side of the Github page at https://github.com/SjoerdB93/GIScan. 

**Linux:** GIScan is currently under the submission process as an application on Flathub. Once that is approved, this is the officially recommended method to install GIScan. In the meantime it can be run directly from source by executing main.py in Python. 

**MacOS:** This tool has only been tested on Linux and Windows, and MacOS is not officially supported. Nevertheless, it *should* work on MacOS by executing the main.py from the terminal using Python. 

**Note**: This tool is in no official way affiliated with Petra III or DESY. This software started as a tool to analyze my own data obtained at this beamline and is mostly developed during my own free time.
