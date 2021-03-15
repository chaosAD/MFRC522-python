# Code by Simon Monk https://github.com/simonmonk/

from . import MFRC522
import RPi.GPIO as GPIO

class SimpleMFRC522:

  READER = None

  KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
  BLOCK_ADDRS = [8, 9, 10]

  def __init__(self):
    self.READER = MFRC522()

  def read(self):
      return self.read_sector(2)

  def read_sector(self, sector):
      id, text = self.read_sector_no_block(sector)
      while not id:
          id, text = self.read_sector_no_block(sector)
      return id, text

  def read_id(self):
    id = self.read_id_no_block()
    while not id:
      id = self.read_id_no_block()
    return id

  def read_id_no_block(self):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None
      return self.uid_to_num(uid)

  def read_no_block(self):
      return self.read_sector_no_block(self, 2)

  def write(self, text):
      return self.write_sector(text, 2)

  def write_sector(self, text, sector):
      id, text_in = self.write_sector_no_block(text, sector)
      while not id:
          id, text_in = self.write_sector_no_block(text, sector)
      return id, text_in

  def write_no_block(self, text):
      return self.write_sector_no_block(text, 2)

  def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n

  def read_sector_no_block(self, sector):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None, None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None, None
      id = self.uid_to_num(uid)
      self.READER.MFRC522_SelectTag(uid)
      block = sector * 4
      blocks = [block, block+1, block +2]
      status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, block + 3, self.KEY, uid)
      data = []
      text_read = ''
      if status == self.READER.MI_OK:
          for block_num in blocks:
              block = self.READER.MFRC522_Read(block_num)
              if block:
                  data += block
          if data:
              text_read = ''.join(chr(i) for i in data)
      self.READER.MFRC522_StopCrypto1()
      return id, text_read

  def write_sector_no_block(self, text, sector):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None, None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None, None
      id = self.uid_to_num(uid)
      self.READER.MFRC522_SelectTag(uid)
      block = sector * 4
      if block == 0:
          blocks = [block+1, block +2]
      else:
          blocks = [block, block+1, block +2]
      status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, block + 3, self.KEY, uid)
      self.READER.MFRC522_Read(block + 3)
      if status == self.READER.MI_OK:
          data = bytearray()
          data.extend(bytearray(text.ljust(len(blocks) * 16).encode('ascii')))
          i = 0
          for block_num in blocks:
              self.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
              i += 1
      self.READER.MFRC522_StopCrypto1()
      return id, text[0:(len(blocks) * 16)]