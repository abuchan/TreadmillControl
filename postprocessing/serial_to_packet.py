from struct import unpack
from ftplib import FTP
from glob import glob
from os import makedirs

# Remote sbRIO address and folder
ftp_addr = '10.0.0.2'
ftp_dir = 'logs'

# Where to find OptitrackLogs
optitrack_dir = ''

# Where collected files get put
logs_dir = './logs/'

# Get the most recent num files, all if num is -1
def fetch_and_parse(num):
   host = FTP(ftp_addr)
   host.login()
   host.cwd(ftp_dir)
   dirlist = []
   host.dir(dirlist.append)
   
   if num is -1:
      file_idx = range(0,len(dirlist),2)
   else:
      file_idx = range(-2*num,0,2)
   
   log_count = 0
   for i in file_idx:
      ctrl_filename = dirlist[i].split()[-1]
      datestring = ctrl_filename[0:19]
      local_dir = logs_dir + datestring + '/'
      
      if len(glob(local_dir)) is not 0:
         print 'Error: %s directory already exists' % datestring
      else:
         makedirs(local_dir)
         local_ctrl_file = open(local_dir + ctrl_filename,'wb')
         host.retrbinary('RETR ' + ctrl_filename, local_ctrl_file.write)
         local_ctrl_file.close()
         
         robot_filename = dirlist[i+1].split()[-1]
         local_robot_file = open(local_dir + robot_filename, 'wb')
         host.retrbinary('RETR ' + robot_filename, local_robot_file.write)
         local_robot_file.close()
         
         parse_datafile(local_dir + robot_filename)
         
         log_count = log_count + 1
      
   print '%d logs read' % log_count
         
def extract_packet(data,index):
   size = ord(data[index])
   size_check = ord(data[index+1])
   
   while(index < len(data) and (size < 5 or size > 200 or (size + size_check) is not 255)):
      index = index + 1
      size = ord(data[index])
      size_check = ord(data[index+1])
   
   packet = data[index : index + size]
   
   bytes = map(ord,list(packet))
   if sum(bytes[0:-1])%256 == bytes[-1]:
      valid = 1
   else:
      valid = 0
      
   return (valid, packet, index + size)

def parse_packet(packet):
   # parse telemetry packet
   if(ord(packet[3]) == 0x83):
      values = unpack('L4l12h', packet[4:-1])
      return ', '.join(map(str,values))
   else:
      return packet.encode('hex')
   
def read_datafile(filename):
   f = open(filename, 'rb')
   d = f.read()
   f.close()
   return d
   
def parse_datafile(filename):
   filename_list = filename.split('.')
   filename_list.insert(-1, 'parsed')
   out_filename = '.'.join(filename_list)
   f_out = open(out_filename,'w')
   f_out.write('time, posL, posR, composL, composR, dcL, dcR, gyroX, gyroY, gyroZ, accelX, accelY, accelZ, bemfL, bemfR, Vbatt, sync\n')
   d = read_datafile(filename)
   i = 0
   while(i<len(d)):
      (valid, packet, i) = extract_packet(d,i)
      if(valid):
         f_out.write(parse_packet(packet) + '\n')
   
   f_out.close()