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
GIScan is a simple tool to open and analyze existing GISAXS data as obtained at the beamline P03 of PETRA III at the DESY Synchrotron in Hamburg. This tool handles raw data directly and does not need any prior data reduction. The accepted input data is in .cbf format, any other data type is unsupported.

Selected data is automatically converted in a mapping of choice as selected in the setting menu, supported mapping types are detector positions in pixels, angular space and q-space. By default, a scan detector-scan is made over the Qy = 0 position as well as an out-of-plane scan near the critical angle of a Ni/Ti multilayer.  

The region of interest (ROI) over which the scans are made can be moved using either the obtained in-plane or the out-of-plane scans. Alternatively a region can be selected by the mouse, or entered manually using the coordinate positions in the bottom-left corner. Using the Background selection, an ROI can be chosen for the background as well and the average background intensity will be substracted from the scans that are made. Both the vertical and the horizontal scan can be exported in plain .txt files for further analysis. 

Furthermore, the full-width-half-maximum (FWHM) of a peak can be obtained as well using a dedicated button. Given time in the future I may implement a simple fitting functionality to seperate the specular and off-specular signal in the in-plane scans from each other so that these corresponding values can be obtained as well.

The software is very functional at the moment, but is still considered to be in beta stage. A proper code clean up needs to be done and documentation is rather limited at the moment. Testing is primarily done on Fedora Silverblue (Linux), but it should be cross-compatible with any modern version of Linux, MacOS or Windows. In the near future I will release packaged versions for both Linux and Windows. The plan is to release this as RPM and hopefully as Flatpak for Linux and as a standalone executable in Windows.

For any support or other questions, please contact me at info@sjoerd.se. Keep in mind that this program comes with 
absolutely no warranty or formal support, but I will try my best to be of assistance. 
