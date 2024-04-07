# NeuroRealTimeProcessing
Map real-time mice neural data to limb coordinates

# Background:
Scanbox, besides saving the '.sbx' image file after a scan session, it also provides the option to generate real-time data as it runs. To that end, it overwrites for every new frame a memory mapped file called 'scanbox.mmap'. The reason it constantly overwrites the same file instead of appending every new frame to it is likely to minimize the memory footprint.

What the scanbox.mmap file contains is the Green PMT (chA), at least as of Feb 2024 in the Dadarlat Lab.

## Step-by-step on how to read data real-time:
1) Set '.mmap' to True in the sbx_config file
2) Open Scanbox
3) Check the 'plug in' box in the Scanbox UI before running
4) After reading a frame using your Python/MATLAB script tell scanbox to move on
   by writing '-1' to the respective index in the Header (reference the mmap_scanbox.py file for that)
5) Save each frame or/and use the frames as you go to do whatever you need
6) Reference the mmap_scanbox.py example code to see how to extract information
   from the memory mapped files.

# Running the example code:
1) Make the required changes to the 'config.ini' file:
    - Adjust the path to the scanbox.mmap file using the 'mmapPath' variable. This file will be saved by Scanbox, so the user has to figure out where it's getting saved. Tip: Look at the mmap folder created by scanbox.
    - Adjust the mouse name and experiment ID. These are used to create the directory with the frames as the code runs.

2) Run the code by writing in your terminal 'python mmap_scanbox.py' BEFORE you start the Scanbox process.

3) When you finish the Scanbox process, the python script will notice it and stop as well by itself. If it doesn't, there was likely a problem reading the frames. 

4) The script will save every frame generated as a CSV file. Additionally, the user may change the code however they want to use the 'chA' variable to serve their own purpose, as that
   is the real-time Green PMT.
