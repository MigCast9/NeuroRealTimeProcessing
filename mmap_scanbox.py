#file name: scanbox.mmap
#iter value that changes for directory (?)
# C:\Users\DadarlatLab\Documents\MATLAB\ScanboxTower1-master\mmap


import numpy as np
import time
import csv
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

MMAP_FILE = 'scanbox.mmap'

mmfile = np.memmap(MMAP_FILE, dtype=np.uint16, mode='r+')

# Assuming header has 16 elements and the rest of the data is in chA and chB
header_size = 16 * np.dtype(np.uint16).itemsize


# Read the header and the rest of the data
header = np.frombuffer(mmfile, dtype=np.int16, count=16)

print(f"File size: {os.path.getsize(MMAP_FILE)}")
print(f"Expeted File size: {16 * 2 + 512*796*2*2}")


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
    
    scalarSumChA = 0
    avgSumChA = 0

    counter = 0
    while True:
        headerData = extractHeaderData()
        currFrame = headerData['frame']
        
        #Remove when done
        mmfile[0] = counter
        ###
        
        #Stay here until new frame comes around
        while currFrame < 0:
            if currFrame == -2: #scanbox stopped
                return
            headerData = extractHeaderData()
            currFrame = headerData['frame']
        
        #Display frame
        print(f"\nValid Frame: {currFrame}\n")
        print(f"Valid Header: {headerData}")
        
        #If its our first time seeing a frame, we extract the dimensions for the channels
        if currFrame == 0:
            nlines = int(headerData['nlines'])            
            ncols = int(headerData['ncols'])
        
        #Extract channels
        chA = extractChannelData(nlines, ncols)

        #Temporary: Play around with channels, e.g create a running sum and running avg
        scalarSumChA += np.sum(chA, dtype=np.uint32)
        avgSumChA = scalarSumChA / (currFrame + 1)
                
        print(f"Scalar Running Sum: {scalarSumChA}")
        print(f"Scalar Running Sum/Cnt: {avgSumChA}")
        
        with open(f'{mouseName}_{experimentID}/frame_{currFrame}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(chA)
        
        #Signal that the frame has been consumed
        mmfile[0] = -1
        
        #Remove when done
        counter += 1
        time.sleep(1)
    

if __name__ == '__main__':   
    #53950_1L_000_531
    # mouseName = input("Mouse name: ")
    # experimentID = input("Experiment ID: ")
    mouseName = '53950_1L_000_531'
    experimentID = 0
    
    directory_path = f'./{mouseName}_{experimentID}'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    # 'C:\Users\DadarlatLab\Documents\MATLAB\ScanboxTower1-master\mmap\scanbox.mmap'
    main(mouseName, experimentID)

    print('\n Done \n')

    #Working: Checked Plug in box
    #Woring: write -1 so matlab scanbox code knows its time for next frame
    #Working: using nohup
    
    del mmfile
