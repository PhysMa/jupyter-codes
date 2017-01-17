# -*- coding: utf-8 -*-
"""
Controls Princeton Instrument Acton SP2300 monochromator

@author: Ouri, Eric
"""
import visa
import time
import re

class pi_commands():
    def __init__(self, com_number): # E.g., if the instrument is at ASRL4, use 4 as com_number
        rm=visa.ResourceManager()
        self.m=rm.open_resource('ASRL'+str(com_number)+'::INSTR', timeout=10000, read_termination='ok\r\n', write_termination='\r') # self.m stores the PyVisa instant pointing to the instrument
        self.m.clear()
        self.nm=self.get_nm(1)

    def close_comm(self):
        self.m.clear()
        self.m.close()

    def get_model_serial(self):
        self.m.clear()
        self.model=self.m.query('MODEL')
        self.serialN=self.m.query('SERIAL')
        return( self.model , self.serialN)

    def get_nm(self,to_print):
        self.m.clear()
        self.curr_nm_reply=self.m.query('?NM')
        temp=re.split(' ',self.curr_nm_reply)
        self.curr_nm=float(temp[1])
        if to_print:
            print(self.curr_nm_reply)
        return self.curr_nm

    def is_done(self):
        self.m.clear()
        self.done=int(self.m.query('MONO-?DONE'))
        return self.done

    def get_speed(self):
        self.m.clear()
        speed=re.split(' ',self.m.query('?NM/MIN'))
        self.speed=float(speed[1])
       # print('scanning speed is '+str(self.speed)+ ' nm/min')
        return self.speed

    def get_active_grating(self):
        self.m.clear()
        self.active_grating=self.m.query('?GRATING')
        return int(self.active_grating)

    def get_available_gratings(self):
        self.m.clear()
        self.m.write('?GRATINGS')
        self.m.read_termination='\n'
        self.available_gratings=[]
        for G in range(5):
            self.available_gratings.append('\n'+self.m.read())
        self.m.clear()
        self.m.read_termination='ok\r\n'
        print (self.available_gratings)
        return self.available_gratings

    def get_mirror(self):
        self.m.clear()
        self.mirror=self.m.query('?MIRROR')
        return self.mirror

    def get_mirror_bool(self):
        self.m.clear()
        self.mirror_bool=int(self.m.query('?MIR'))
        return self.mirror_bool

        #mirror control
    def set_out_mirror(self,mirror_state):
        self.m.write('EXIT-MIRROR')
        self.m.write(mirror_state)
        time.sleep(2)
        self.m.clear()
        state=pi_commands.get_mirror(self)
        if state == ' '+ mirror_state+'  ':
            print([' output mirror in %s state' %(mirror_state)])
        else:
            print('Error in output mirror positioning')
        return

    def set_in_mirror(self,mirror_state):
        self.m.write('ENT-MIRROR')
        self.m.write(mirror_state)
        time.sleep(2)
        self.m.clear()
        state=pi_commands.get_mirror(self)
        if state == ' '+mirror_state+'  ':
            print('input mirror in %s state' %(mirror_state))
        else:
            print('Error in input mirror positioning')
        return

    #Grating control
    def set_grating(self, gratingN):
        self.m.timeout=30000
        curr_gr=(pi_commands.get_active_grating(self))
        self.m.write(str(gratingN)+' GRATING')
        time.sleep(20)
        self.m.timeout=2000
        curr_gr=(pi_commands.get_active_grating(self))

        if curr_gr!=gratingN:
            print('Error in grating selection')
            return
        pi_commands.get_available_gratings(self)
        return

        #Wavelength positioning control
    def set_NM(self, wavelength):
        step=wavelength-self.nm
        step=int(step*1000)
        step=step/1000
        self.m.write(str(step)+' >NM')
        done_move=0

        while done_move==0:
            done_move=pi_commands.is_done(self)
            time.sleep(1)

        self.nm+=self.get_nm(0)
        print('tuned wavelength is: '+str(self.nm) )
        return

    def set_speed(self, speed):
        curr_speed=pi_commands.get_speed(self)
        self.m.write(str(speed)+' NM/MIN')

        count_max=10
        count=0
        while curr_speed!=speed:
            self.m.clear()
            if count>count_max:
                print('Error in speed setting')
                return
            curr_speed=pi_commands.get_speed(self)
            time.sleep(1)
            count=count+1
        print('set scaning speed is: '+str(pi_commands.get_speed(self))+ ' nm/min')
        return

        #initialization setting
    def initial_config(self, gratingN, wavelength, speed) :
        self.m.write(str(speed)+' INIT-SRATE')
        self.m.write(str(gratingN)+' INIT-GRATING')
        self.m.write(str(wavelength)+' INIT-WAVELENGTH')
        return

        #calibration methods
    def cal_offset(self, gratingN, offset):
        self.m.write(str(offset)+' '+str(gratingN-1)+' INIT-OFFSET')
        self.m.write('MONO-RESET')
        return

    def cal_gadjust(self, gratingN, adjust ):
        self.m.write(str(adjust)+' '+str(gratingN-1)+'INIT-GADJUST')
        self.m.write('MONO-RESET')
        return
