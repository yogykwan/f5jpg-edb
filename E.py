# -*- coding: utf-8 -*-
# -*- by: Yogy Kwan -*-

import logging
import math
import random
from PIL import Image
from B import AAN
from B import QUANTUM
from B import BITS
from B import VAL
from B import ZIGZAG

logger=logging.getLogger('encoder')

def create(value=None, *args):
    if len(args) and args[0]:
        return [create(value,*args[1:]) for i in range(round(args[0]))]
    else: return value

class jpegEncoder(object):
    comp_num=3
    hsamp_factor=[2,1,1]
    vsamp_factor=[2,1,1]
    qtable_number=[0,1,1]
    dctable_number=[0,1,1]
    actable_number=[0,1,1]
    def __init__(self,image,quality,out,comment):
        logger.info('initing input image')
        self.image=image
        self.image_width,self.image_height=image.size
        self.quality=quality
        self.out=out
        self.comment=comment
        self.getYcc()
        self.initDct()
        self.initHuff()
        self.getCoeff()

    def getYcc(self):
        max_hsamp_factor=max(self.hsamp_factor)
        max_vsamp_factor=max(self.vsamp_factor)
        self.comp=create(None,self.comp_num)
        self.comp_width=create(0,self.comp_num)
        self.comp_height=create(0,self.comp_num)
        self.block_width=create(0,self.comp_num)
        self.block_height=create(0,self.comp_num)
        for i in range(self.comp_num):
            self.comp_width[i]=int(math.ceil(self.image_width/8)*8)
            self.comp_width[i]=int(self.comp_width[i]/max_hsamp_factor*self.hsamp_factor[i])
            self.block_width[i]=int(math.ceil(self.comp_width[i]/8))
            self.comp_height[i]=int(math.ceil(self.image_height/8)*8)
            self.comp_height[i]=int(self.comp_height[i]/max_vsamp_factor*self.vsamp_factor[i])
            self.block_height[i]=int(math.ceil(self.comp_height[i]/8))
        Y=create(0,self.comp_height[0],self.comp_width[0])
        Cb=create(0,self.comp_height[0],self.comp_width[0])
        Cr=create(0,self.comp_height[0],self.comp_width[0])
        for y in range(self.image_height):
            for x in range(self.image_width):
                r,g,b=self.image.getpixel((x,y))
                Y[y][x]=0.299*r+0.587*g+0.114*b
                Cb[y][x]=-0.16874*r-0.33126*g+0.5*b+128
                Cr[y][x]=0.5*r-0.41869*g-0.08131*b+128
        Cb=[[Cb[row<<1][col<<1] for col in range(self.comp_width[1])] for row in range(self.comp_height[1])]
        Cr=[[Cr[row<<1][col<<1] for col in range(self.comp_width[2])] for row in range(self.comp_height[2])]
        self.comp=[Y,Cb,Cr]

    def initDct(self):
        self.quantum=create(0,2,64)
        self.divisors=create(0,2,64)
        if self.quality<=0: quality=1
        elif self.quality>100: qulity=100
        elif self.quality<50: quality=5000/self.quality
        else: quality=200-self.quality*2
        for i in range(2):
            self.quantum[i]=[]
            for q in QUANTUM[i]:
                p=(q*quality+50)/100
                if p<=0: self.quantum[i].append(1)
                elif p>255: self.quantum[i].append(255)
                else: self.quantum[i].append(p)
            self.divisors[i]=[]
            for j in range(len(self.quantum[i])):
                self.divisors[i].append(8*AAN[j%8]*AAN[j//8]*self.quantum[i][j])
         
    def initHuff(self):
        self.dc=create(0,2,12,2)
        self.ac=create(0,2,255,2)
        def cal(bits,val,matrix):
            p=0
            code=0
            for l in range(1,17):
                for i in range(bits[l]):
                    matrix[val[p]]=[code,l]
                    p+=1
                    code+=1
                code<<=1
        for i in range(2):
            cal(BITS[i<<1],VAL[i<<1],self.dc[i])
            cal(BITS[i<<1|1],VAL[i<<1|1],self.ac[i])
                            
    def forwardDct(self,indata,q_num):
        output=[[indata[i][j]-128 for j in range(8)] for i in range(8)]
        tmp=create(0,14)
        for i in range(8):
            for j in range(4):
                tmp[j]=output[i][j]+output[i][7-j]
                tmp[7-j]=output[i][j]-output[i][7-j]
            tmp[10]=tmp[0]+tmp[3]
            tmp[11]=tmp[1]+tmp[2]
            tmp[12]=tmp[1]-tmp[2]
            tmp[13]=tmp[0]-tmp[3]
            output[i][0]=tmp[10]+tmp[11]
            output[i][4]=tmp[10]-tmp[11]
            z1=(tmp[12]+tmp[13])*0.707106781
            output[i][2]=tmp[13]+z1
            output[i][6]=tmp[13]-z1
            tmp[10]=tmp[4]+tmp[5]
            tmp[11]=tmp[5]+tmp[6]
            tmp[12]=tmp[6]+tmp[7]
            z5=(tmp[10]-tmp[12])*0.382683433
            z2=0.541196100*tmp[10]+z5
            z4=1.306562965*tmp[12]+z5
            z3=tmp[11]*0.707106781
            z11=tmp[7]+z3
            z13=tmp[7]-z3
            output[i][5]=z13+z2
            output[i][3]=z13-z2
            output[i][1]=z11+z4
            output[i][7]=z11-z4
        for i in range(8):
            for j in range(4):
                tmp[j]=output[j][i]+output[7-j][i]
                tmp[7-j]=output[j][i]-output[7-j][i]
            tmp[10]=tmp[0]+tmp[3]
            tmp[11]=tmp[1]+tmp[2]
            tmp[12]=tmp[1]-tmp[2]
            tmp[13]=tmp[0]-tmp[3]
            output[0][i]=tmp[10]+tmp[11]
            output[4][i]=tmp[10]-tmp[11]
            z1=(tmp[12]+tmp[13])*0.707106781
            output[2][i]=tmp[13]+z1
            output[6][i]=tmp[13]-z1
            tmp[10]=tmp[4]+tmp[5]
            tmp[11]=tmp[5]+tmp[6]
            tmp[12]=tmp[6]+tmp[7]
            z5=(tmp[10]-tmp[12])*0.382683433
            z2=0.541196100*tmp[10]+z5
            z4=1.306562965*tmp[12]+z5
            z3=tmp[11]*0.707106781
            z11=tmp[7]+z3
            z13=tmp[7]-z3
            output[5][i]=z13+z2
            output[3][i]=z13-z2
            output[1][i]=z11+z4
            output[7][i]=z11-z4
        ans=[]
        for i in range(8):
            for j in range(8):
                ans.append(round(output[i][j]/self.divisors[q_num][i*8+j]))
        self.coeff.extend(ans)
    
    def getCoeff(self):
        logger.info('calculating coeff')
        dct_array=create(0,8,8)
        self.coeff=[]
        max_hsamp_factor=max(self.hsamp_factor)
        max_vsamp_factor=max(self.vsamp_factor)
        for r in range(min(self.block_height)):
            for c in range(min(self.block_width)):
                xpos,ypos=c*8,r*8
                for comp in range(self.comp_num):
                    indata=self.comp[comp]
                    maxa=self.image_height/max_vsamp_factor*self.vsamp_factor[comp]-1
                    maxb=self.image_width/max_hsamp_factor*self.hsamp_factor[comp]-1
                    for i in range(self.vsamp_factor[comp]):
                        for j in range(self.hsamp_factor[comp]):
                            ia=ypos*self.vsamp_factor[comp]+i*8
                            ib=xpos*self.hsamp_factor[comp]+j*8
                            for a in range(8):
                                for b in range(8):
                                    dct_array[a][b]=indata[int(min(ia+a,maxa))][int(min(ib+b,maxb))]
                            self.forwardDct(dct_array,self.qtable_number[comp])

    def write_array(self,data):
        length=((data[2]&0xff)<<8)+(data[3]&0xff)+2
        self.out.write(bytearray(data[:length]))
                                     
    def writeHeads(self):
        logger.info('writing new image')
        SOI=[0xff,0xd8]
        self.out.write(bytearray(SOI))
        
        APP=[0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 
             0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 
             0x00, 0x60, 0x00, 0x60, 0x00, 0x00]
        self.write_array(APP)
        
        comment=self.comment
        if comment:
            length=len(comment)+2
            COM=[0xff,0xfe,length>>8&0xff,length&0xff]
            comment=[ord(i) for i in comment]
            COM.extend(comment)
            self.write_array(COM)
            
        DQT=[0xff,0xdb,0x00,0x84]
        for k in range(2):
            DQT.append(k)
            DQT.extend([int(self.quantum[k][ZIGZAG[i]]) for i in range(64)])
        self.write_array(DQT)

        SOF=[0xff,0xc0,0x00,0x11,0x08, 
             self.image_height>>8&0xff,self.image_height&0xff, 
             self.image_width>>8&0xff,self.image_width&0xff, 
             self.comp_num]
        for i in range(self.comp_num):
            SOF.append(i+1)
            SOF.append(self.hsamp_factor[i]<<4|self.vsamp_factor[i])
            SOF.append(self.qtable_number[i])
        self.write_array(SOF)
        
        DHT=[0xff,0xc4,0,0]
        for i in range(4):
            DHT.extend(BITS[i])
            DHT.extend(VAL[i])
        DHT[2]=len(DHT)-2>>8&0xff
        DHT[3]=len(DHT)-2&0xff
        self.write_array(DHT)

        SOS=[0xff,0xda,0x00,0x0c,self.comp_num]
        for i in range(self.comp_num):
            SOS.append(i+1)
            SOS.append(self.dctable_number[i]<<4|self.actable_number[i])
        SOS.extend([0x00,0x3f,0x00])
        self.write_array(SOS)
        
    def buffer_it(self,code,size):
        put_buffer=code
        put_bits=self.buffer_put_bits+size
        put_buffer&=(1<<size)-1
        put_buffer<<=24-put_bits
        put_buffer|=self.buffer_put_buffer
        while put_bits>=8:
            c=put_buffer>>16&0xff
            self.out.write(bytearray([c]))
            if c==0xff: self.out.write(bytearray([0]))
            put_buffer<<= 8
            put_bits-=8
        self.buffer_put_buffer=put_buffer
        self.buffer_put_bits=put_bits
        
    def huffEncode(self,zigzag,prec,dc_code,ac_code):
        tmp=tmp2=zigzag[0]-prec
        if tmp<0:
            tmp=-tmp
            tmp2-=1
        nbits=0
        while tmp:
            nbits+=1
            tmp>>=1
        self.buffer_it(*self.dc[dc_code][nbits])
        if nbits: self.buffer_it(tmp2,nbits)
        r=0
        for k in range(1,64):
            tmp=zigzag[ZIGZAG[k]]
            if tmp==0: r+=1
            else:
                while r>15:
                    self.buffer_it(*self.ac[ac_code][0xf0])
                    r-=16
                tmp2=tmp
                if tmp<0:
                    tmp=-tmp
                    tmp2-=1
                nbits=0
                while tmp:
                    nbits+=1
                    tmp>>=1
                i=(r<<4)+nbits
                self.buffer_it(*self.ac[ac_code][i])
                self.buffer_it(tmp2,nbits)
                r=0
        if r>0: self.buffer_it(*self.ac[ac_code][0])
        
    def writeImage(self):
        logger.info('huffman coding')
        index=0
        self.buffer_put_buffer=0
        self.buffer_put_bits=0
        last_dc_value=create(0,self.comp_num)
        for r in range(min(self.block_height)):
            for c in range(min(self.block_width)):
                for comp in range(self.comp_num):
                    for i in range(self.vsamp_factor[comp]):
                        for j in range(self.hsamp_factor[comp]):
                            dct_array=self.coeff[index:index+64]
                            self.huffEncode(dct_array,last_dc_value[comp],self.dctable_number[comp],self.actable_number[comp])
                            last_dc_value[comp]=dct_array[0]
                            index+=64
        put_buffer=self.buffer_put_buffer
        put_bits=self.buffer_put_bits
        while put_bits>0:
            c=put_buffer>>16&0xff
            self.out.write(bytearray([c]))
            if c==0xff: self.out.write(bytearray([0]))
            put_buffer<<=8
            put_bits-=8
        EOI=[0xff,0xd9]
        self.out.write(bytearray(EOI))
        
class encoder(object):
    def __init__(self,image,quality,out,comment):
        self.out=out
        self.iJpegE=jpegEncoder(image,quality,out,comment)

    def write(self,level,data,password):
        self.data=data
        self.password=password
        self.iJpegE.writeHeads()
        if level=='3': self.embedData3()
        elif level=='4': self.embedData4()
        elif level=='5': self.embedData5()
        self.iJpegE.writeImage()

    def embedData3(self):
        logger.info('embedding data in image by f3')
        coeff=self.iJpegE.coeff
        byte_embed=len(self.data)
        if byte_embed>0x7fffffff: byte_embed=0x7fffffff
        logger.info('totally %d bytes to embed by f3'%len(self.data))
        bit_embed=byte_embed&1
        byte_embed>>=1
        need_embed=31
        data_index=0
        for i,j in enumerate(coeff):
            if i%64==0 or j==0: continue
            if j>0 and (j&1)!=bit_embed: coeff[i]-=1
            elif j<0 and (j&1)!=bit_embed: coeff[i]+=1
            if coeff[i]!=0:
                if need_embed==0:
                    if data_index>=len(self.data): break
                    byte_embed=ord(self.data[data_index])
                    data_index+=1
                    need_embed=8
                bit_embed=byte_embed&1
                byte_embed>>=1
                need_embed-=1
                
    def embedData4(self):
        logger.info('embedding data in image by f4')
        coeff=self.iJpegE.coeff
        byte_embed=len(self.data)
        if byte_embed>0x7fffffff: byte_embed=0x7fffffff
        logger.info('totally %d bytes to embed by f4'%len(self.data))
        bit_embed=byte_embed&1
        byte_embed>>=1
        need_embed=31
        data_index=0
        for i,j in enumerate(coeff):
            if i%64==0 or j==0: continue
            if j>0 and (j&1)!=bit_embed: coeff[i]-=1
            elif j<0 and (j&1)==bit_embed: coeff[i]+=1
            if coeff[i]!=0:
                if need_embed==0:
                    if data_index>=len(self.data): break
                    byte_embed=ord(self.data[data_index])
                    data_index+=1
                    need_embed=8
                bit_embed=byte_embed&1
                byte_embed>>=1
                need_embed-=1
                
    def embedData5(self):
        logger.info('embedding data in image by f5')
        self.permutate()
        self.matrixCode()

    def permutate(self):
        logger.info('permutating')
        random.seed(self.password)
        size=len(self.iJpegE.coeff)
        self.shuffle=[i for i in range(size)]
        for i in range(size):
            index=self.getInt(size)
            size-=1
            self.shuffle[size],self.shuffle[index]=self.shuffle[index],self.shuffle[size]

    def matrixCode(self):
        logger.info('matrix coding')
        coeff=self.iJpegE.coeff
        coeff_num=len(coeff)
        one,zero=0,0
        for i,j in enumerate(coeff):
            if i%64==0: continue
            elif j==1 or j==-1: one+=1
            elif j==0: zero+=1
        other=coeff_num-one-zero-coeff_num//64
        expect=int(0.5*one)+other
        byte_embed=len(self.data)
        if byte_embed>0x7fffff: byte_embed=0x7fffff
        for i in range(1,10):
            n=(1<<i)-1
            use=(expect//n)*i/8
            if use<byte_embed+4: 
                i=i-1
                break
        k=i
        n=(1<<k)-1
        if n==0:
            logger.info('file not suitable')
            n=1
        else: logger.info('using (1,%d,%d) code'%(n,k))
        logger.info('totally %d bytes to embed by f5'%byte_embed)
        byte_embed|=k<<24
        for i in range(4): byte_embed^=self.getByte()<<i*8
        bit_embed=byte_embed&1
        byte_embed>>=1
        need_embed=31
        data_index=0
        shuffle_pos=0
        for j in self.shuffle:
            shuffle_pos+=1
            if j%64==0 or coeff[j]==0: continue
            if coeff[j]>0 and (coeff[j]&1)!=bit_embed: coeff[j]-=1
            elif coeff[j]<0 and (coeff[j]&1)==bit_embed: coeff[j]+=1
            if coeff[j]!=0:
                if need_embed==0: break;
                bit_embed=byte_embed&1
                byte_embed>>=1
                need_embed-=1
        try:
            while True:
                kbits_embed=0
                for i in range(k):
                    if need_embed==0:
                        if data_index>=len(self.data): break
                        byte_embed=ord(self.data[data_index])^self.getByte()
                        data_index+=1
                        need_embed=8
                    bit_embed=byte_embed&1
                    byte_embed>>=1
                    need_embed-=1
                    kbits_embed|=bit_embed<<i
                refer=create(0,n)
                for i in range(n):
                    while self.shuffle[shuffle_pos]%64==0 or coeff[self.shuffle[shuffle_pos]]==0:
                        shuffle_pos+=1
                    refer[i]=self.shuffle[shuffle_pos]
                    shuffle_pos+=1
                while True:
                    fhash=0
                    for i,j in enumerate(refer):
                        if coeff[j]>0: tmp=coeff[j]&1
                        else: tmp=coeff[j]&1^1
                        if tmp==1: fhash^=i+1
                    d=fhash^kbits_embed
                    if d==0: break
                    s=refer[d-1]
                    if coeff[s]>0: coeff[s]-=1
                    elif coeff[s]<0: coeff[s]+=1
                    if coeff[s]==0:
                        refer[d-1:d]=[]
                        while self.shuffle[shuffle_pos]%64==0 or coeff[self.shuffle[shuffle_pos]]==0:
                            shuffle_pos+=1
                        refer.append(self.shuffle[shuffle_pos])
                        shuffle_pos+=1
                    else: break
                if data_index>=len(self.data) and need_embed==0: break
        except IndexError:
            logger.info('data is too long')
            
    def getByte(self):
        return random.randint(-128,127)
    
    def getInt(self,max_value):
        ret_val=self.getByte()|self.getByte()<<8|self.getByte()<<16|self.getByte()<<24
        ret_val%=max_value
        if ret_val<0: ret_val+=max_value
        return ret_val
    

        
