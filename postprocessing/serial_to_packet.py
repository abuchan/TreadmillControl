from struct import *

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