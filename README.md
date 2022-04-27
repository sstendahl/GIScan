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
Simple tool to read and analyze existing GISAXS data. This software has only been tested on raw GISXAS-data obtained at
DESY in Germany in .cbf format. Any other type of data is unsupported. While the program is mostly feature complete at
the moment, it is still at an early alpha stage. 

Imported data is converted to angular coordinates by default. Right now, the needed experimental parameters for this
conversion are hard-coded to be equal to the parameters in my own experimental run. A settings window to change these 
parameters is next on the planned features list.
An option to convert to q-space, or take the raw-data as-is from pixel coordinates will be added eventually as well.

Note that this is an alpha version. The code is messy at the moment, a proper code clean up as well as some
documentation need to be done before declaring version 1.0. Testing is primarily done on Fedora Silverblue (Linux), but
this software should be compatible with any modern version of Linux, MacOS or Windows.