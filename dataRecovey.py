import os
import threading
import time
from pathlib import Path
global letter, recoveredLocation, available_drives, total_iteration

file_formats = {
    #======= IMAGES =====#
    'jpg': {'enabled': 1, 'start': b'\xff\xd8\xff\xe0\x00\x10\x4a\x46', 'end': b'\xff\xd9', 'offset': 2},
    'png': {'enabled': 1, 'start': b'\x89\x50\x4e\x47', 'end': b'\x49\x45\x4e\x44\xae\x42\x60\x82', 'offset': 8},
    'jpeg': {'enabled': 1, 'start': b'\xff\xd8\xff\xe0', 'end': b'\xff\xd9', 'offset': 2},
    'bmp': {'enabled': 1, 'start': b'\x42\x4d', 'end': b'\x00\x00\x00\x00', 'offset': 0},
    'gif': {'enabled': 1, 'start': b'\x47\x49\x46\x38', 'end': b'\x3b', 'offset': 0},

    #======= ARCHIVES =====#
    'zip': {'enabled': 1, 'start': b'\x50\x4b\x03\x04\x14', 'end': b'\x50\x4b\x05\x06', 'offset': 4},
    'rar': {'enabled': 1, 'start': b'\x52\x61\x72\x21\x1a\x07', 'end': b'\x00\x00\x00\x00', 'offset': 0},
    '7z': {'enabled': 1, 'start': b'\x37\x7a\xbc\xaf\x27\x1c', 'end': b'\x00\x00\x00\x00', 'offset': 0},
    'tar': {'enabled': 1, 'start': b'\x75\x73\x74\x61\x72', 'end': b'\x00\x00\x00\x00', 'offset': 0},

    #======= VIDEOS =====#
    'mp4': {'enabled': 1, 'start': b'\x66\x74\x79\x70\x69\x73\x6f\x6d', 'end': b'\x6d\x64\x61\x74', 'offset': 4},
    'avi': {'enabled': 1, 'start': b'\x52\x49\x46\x46', 'end': b'\x4c\x49\x53\x54', 'offset': 0},
    'mkv': {'enabled': 1, 'start': b'\x1a\x45\xdf\xa3', 'end': b'\x42\x82', 'offset': 0},
    'mov': {'enabled': 1, 'start': b'\x6d\x6f\x6f\x76', 'end': b'\x66\x72\x65\x65', 'offset': 0},
    'flv': {'enabled': 1, 'start': b'\x46\x4c\x56\x01', 'end': b'\x46\x4c\x56\x02', 'offset': 0},
    'webm': {'enabled': 1, 'start': b'\x1a\x45\xdf\xa3', 'end': b'\x42\x82', 'offset': 0},

    #======= DOCUMENTS =====#
    'pdf': {'enabled': 0, 'start': b'\x25\x50\x44\x46\x2D', 'end': b'\x0a\x25\x25\x45\x4f\x46', 'offset': 6},
    'docx': {'enabled': 1, 'start': b'\x50\x4b\x03\x04\x14', 'end': b'\x50\x4b\x05\x06', 'offset': 4},
    'xlsx': {'enabled': 1, 'start': b'\x50\x4b\x03\x04\x14', 'end': b'\x50\x4b\x05\x06', 'offset': 4},
    'pptx': {'enabled': 1, 'start': b'\x50\x4b\x03\x04\x14', 'end': b'\x50\x4b\x05\x06', 'offset': 4},

    #======= AUDIO =====#
    'mp3': {'enabled': 1, 'start': b'\x49\x44\x33', 'end': b'\x54\x41\x49\x46\x00', 'offset': 0},
    'wav': {'enabled': 1, 'start': b'\x52\x49\x46\x46', 'end': b'\x57\x41\x56\x45', 'offset': 0},
    'flac': {'enabled': 1, 'start': b'\x66\x4c\x61\x43', 'end': b'\x00\x00\x00\x00', 'offset': 0},
    'ogg': {'enabled': 1, 'start': b'\x4f\x67\x67\x53', 'end': b'\x00\x00\x00\x00', 'offset': 0},
}


class Recovery:
    def __init__(self, filetype):
        self.filetype = filetype

    def DataRecovery(self, fileName, fileStart, fileEnd, fileOffSet):
        self._fileName = fileName
        self._fileStart = fileStart
        self._fileEnd = fileEnd
        self._fileOffSet = fileOffSet

        drive = f"\\\\.\\{letter}:"
        fileD = open(drive, "rb")
        size = 512
        byte = fileD.read(size)
        offs = 0
        drec = False
        rcvd = 0

        format_folder = recoveredLocation / self._fileName
        format_folder.mkdir(exist_ok=True) 

        while byte:
            found = byte.find(self._fileStart)
            if found >= 0:
                drec = True
                print(f'==== Found {self._fileName} at location: ' + str(hex(found+(size*offs))) + ' ====') 
                fileN = open(f'{format_folder}\\' + str(rcvd) + f'.{self._fileName}', "wb")
                fileN.write(byte[found:])
                while drec:
                    byte = fileD.read(size)
                    bfind = byte.find(self._fileEnd)
                    if bfind >= 0:
                        fileN.write(byte[:bfind+self._fileOffSet])
                        fileD.seek((offs+1)*size)
                        print(f'==== Wrote {self._fileName} to location: {rcvd}.{self._fileName} ====')

                        drec = False
                        rcvd += 1
                        fileN.close()
                    else: fileN.write(byte)
            byte = fileD.read(size)
            offs += 1
        fileD.close()

total_iteration = 50

available_drives = [ chr(x) + "" for x in range(65,91) if os.path.exists(chr(x) + ":") ]
cwd = Path.cwd()
recoveredLocation = cwd / 'RecoveredData'
recoveredLocation.mkdir(exist_ok=True)
print(f'Recoved data will be saved to {recoveredLocation}')
print(f"Available Drives are: {available_drives}")

recovery_objects = {fmt: Recovery(fmt) for fmt, settings in file_formats.items() if settings['enabled']}

while True:
    letter = input("Enter Removable Drive Letter Or 'Exit' to quit the program: ").capitalize()
    if letter == "Exit" or letter == "exit" or letter == "EXIT":
        break
    elif letter[0] in available_drives:
        for i in range(total_iteration + 1):
            time.sleep(0.1)

        threads = []
        for fmt, settings in file_formats.items():
            if settings['enabled']:
                thread = threading.Thread(
                    target=recovery_objects[fmt].DataRecovery, 
                    args=(fmt, settings['start'], settings['end'], settings['offset'])
                )
                threads.append(thread)
                thread.start()

        startpy = time.time()
        for thread in threads:
            thread.join()
        endpy = time.time()
        print(f"Time taken: {endpy-startpy} seconds")
