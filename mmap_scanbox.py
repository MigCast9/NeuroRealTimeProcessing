#file name: scanbox.mmap
#iter value that changes for directory (?)
# C:\Users\DadarlatLab\Documents\MATLAB\ScanboxTower1-master\mmap


import numpy as np
import time
import csv
import configparser
import os


# mmfile.Data.header(1) = -1;                 % frame or frame #
# % -1, not started
# % -2, stopped
# % 0...N frame number
# mmfile.Data.header(2) = int16(nlines);      % number of lines
# mmfile.Data.header(3) = int16(ncol);        % number of columns
# mmfile.Data.header(4) = 0;                  % TTL corresponding to stimulus
# mmfile.Data.header(5) = int16(handles.volscan.Value);   % volumetric scanning flag

# if ~isempty(handles.vol_table.Data)
#     p = sum([handles.vol_table.Data{:,5}]);
# else
#     p = 1;
# end

# mmfile.Data.header(6) = int16(p);   % period of volumetric wave

# % mmfile.Data.header(6) = int16(str2double(handles.optoperiod.String));   % period of volumetric wave
# mmfile.Data.header(7) = handles.plugin.Value; % code for plugin id #
# mmfile.Data.header(8) = int16(unit);
# mmfile.Data.header(9) = int16(experiment);
# mmfile.Data.header(10) = uint16(handles.meso_check.Value);  % mesoscope enabled?
# mmfile.Data.header(11) = uint16(handles.meso_type.Value);   % what type?
# mmfile.Data.header(12) = uint16(size(handles.roitable.Data,1));   % # of ROIs
# for w=1:length(stim_id)
#     mmfile.Data.header(12+w) = int16(stim_id(w));                    % stimulus id [13 14 15 16] up to 4 numbers
# end

MMAP_FILE = '../scanbox.mmap'

mmfile = np.memmap(MMAP_FILE, dtype=np.uint16, mode='r+')

# Assuming header has 16 elements and the rest of the data is in chA and chB
header_size = 16 * np.dtype(np.uint16).itemsize

# Read the header and the rest of the data
header = np.frombuffer(mmfile, dtype=np.int16, count=16)

#Returns a dictionary with the header information: look at variable definition to see how to access dict
def extractHeaderData():
    
    headerData = {
        'frame':header[0],
        'nlines':header[1],
        'ncols':header[2],
        'TTL':header[3],
        'volumetric':header[4],
        'period':header[5],
        'code_plugin_id':header[6],
        'unit':header[7],
        'experiment':header[8],
        'mesoscope_enabled':header[9],
        'type':header[10],
        'num_roi':header[11],
        'stimulus_1':header[12],
        'stimulus_2':header[13],
        'stimulus_3':header[14],
        'stimulus_4':header[15]
    }


    return headerData

def extractChannelData(nlines, ncols):
    chA = np.frombuffer(mmfile, dtype=np.uint16, count=nlines * ncols, offset=header_size)
    chA = chA.reshape((nlines, ncols))
    
    return chA


def main(mouseName, experimentID):
    
    nlines = 512
    ncols = 796
            
    while True:
        headerData = extractHeaderData()
        currFrame = headerData['frame']
        
        #Stay here until new frame comes around
        while currFrame < 0:
            if currFrame == -2: #scanbox stopped
                return
            headerData = extractHeaderData()
            currFrame = headerData['frame']
        
        #If its our first time seeing a frame, we extract the dimensions for the channels
        if currFrame == 0:
            nlines = int(headerData['nlines'])            
            ncols = int(headerData['ncols'])
        
        #Extract channels
        chA = extractChannelData(nlines, ncols)
        
        #Signal that the frame has been consumed
        mmfile[0][0] = -1
        
        #####################################################################################
        #Use the data
        
        
        
        #####################################################################################
        
        
        
        #Save each frame for future use if necessary
        with open(f'{mouseName}_{experimentID}/frame_{currFrame}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(chA)
        
        

if __name__ == '__main__':   
    #Get config data
    configPath = './config.ini'
    cfg = configparser.RawConfigParser(allow_no_value=True)
    cfg.read(configPath)
    mouseName = cfg.get('name', 'miceName')
    experimentID = cfg.get('experiment_id', 'experimentID')
    
    #Create directory path to save frames
    directory_path = f'./{mouseName}_{experimentID}'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    #######################################
    #Start operations
    #######################################
    
    # 'C:\Users\DadarlatLab\Documents\MATLAB\ScanboxTower1-master\mmap\scanbox.mmap'
    main(mouseName, experimentID)

    print('\n Done \n')

    #Working: Checked Plug in box
    #Woring: write -1 so matlab scanbox code knows its time for next frame
    
    del mmfile
