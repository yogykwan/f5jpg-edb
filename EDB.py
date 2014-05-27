# -*- coding: utf-8 -*-
# -*- by: Yogy Kwan -*-

import sys
import os
import io
import argparse
import logging
from PIL import Image
from E import encoder
from D import decoder

logger=logging.getLogger('edb')
    
parser=argparse.ArgumentParser(
formatter_class=argparse.RawDescriptionHelpFormatter,
description=r'''F5 Steganography EDB
                      __------__
                    /~          ~\
                   |    //^\\//^\|    
                 /~~\  ||  o| |o|:~\
                | |6   ||___|_|_||:|
                 \__.  /      o  \/'
                  |   (       O   )
         /~~~~\    `\  \         /
        | |~~\ |     )  ~------~`\
       /' |  | |   /     ____ /~~~)\
      (_/'   | | |     /'    |    ( |
             | | |     \    /   __)/ \
             \  \ \      \/    /' \   `\
               \  \|\        /   | |\___|
                 \ |  \____/     | |
                 /^~>  \        _/ <
                |  |         \       \
                |  | \        \        \
                 -^-\  \       |        )
                     `\_______/^\______/  ''',
usage='%(prog)s [options] [args]')
parser.add_argument('-t','--type',type=str,default='e',help='input "e" for encode, "d" for decode')
parser.add_argument('-l','--level',type=str,default='5',help='input x for fx steganography')
parser.add_argument('-i','--image',type=str,help='input file')
parser.add_argument('-d','--data',type=str,help='input data')
parser.add_argument('-f','--datafile',type=str,help='input data file')
parser.add_argument('-o','--output',type=str,help='output file')
parser.add_argument('-p','--password',type=str,default='111111',help='input password')
parser.add_argument('-c','--comment',type=str,default='by: Yogy Kwan',help='comment on image')
parser.add_argument('-q','--quiet',action='store_true',help='execute without loggging')
parser.add_argument('-v','--verbose',action='store_true',help='turn on verbose mode')

#options=parser.parse_args(['-i','no.jpg','-f','in.txt','-o','no1.jpg','-l','5'])
#options=parser.parse_args(['-i','no1.jpg','-t','d','-p','111111','-o','out.txt','-l','5'])
options=parser.parse_args()

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s [%(name)s] %(message)s',
                        level=options.quiet and logging.ERROR or options.verbose and logging.DEBUG or logging.INFO)
    if options.image and os.path.isfile(options.image):
        if options.type=='e':
            image=Image.open(options.image)
            if not options.data and not options.datafile:
                print('no data')
                parser.print_help()
                sys.exit(0)
            if options.data: data=options.data
            elif options.datafile:
                txt=open(options.datafile,'r')
                data=''.join(txt)
            if not options.output:
                logger.info('no output file, create output.jpg defaultly')
                options.output='output.jpg'
            if os.path.exists(options.output) and os.path.isfile(options.output):
                print('output file exists, rewrite it?')
                rewrite=input('y/n: ')
                if rewrite=='n': options.output=input('input output file: ')
            output=open(options.output,'wb')
            logger.info('begin EDB steganography')
            iEncoder=encoder(image,80,output,options.comment)
            iEncoder.write(options.level,data,options.password)
            output.close()
            logger.info('all done')
        elif options.type=='d':
            if options.output: output=open(options.output,'w')
            else: output=io.StringIO()
            image=open(options.image,'rb')
            iDecoder=decoder(image.read(),output)
            iDecoder.read(options.level,options.password)
            if not options.output: print(output.getvalue())
            image.close()
            output.close()
    else:
        logger.info('no image')
        parser.print_help()

