#!/usr/bin/env pypy

import sys
import os
import io
import functools



class LFSR:
    def __init__(self, length, clocking, tapped):
        self.reg = [0] * length
        self.clocking = clocking
        self.tapped = list(tapped)

    def print_(self):
        print(self.reg)

    def round_(self, mode, bit=0):
        # irregular clocking: hold the register if clocking == major bit
        if mode == 1 and bit != self.reg[self.clocking]:
            return

        # magic!
        feedback = functools.reduce(lambda x,y: x^y,
                       [self.reg[i] for i in self.tapped])

        # ignore irregular clocking mode
        if mode == 0:
            feedback = feedback ^ bit

        # prefix the feedback bit and shift right for one bit
        self.reg = [feedback] + self.reg[:-1]


class A5_1:
    def __init__(self, session_key, frame_counter):

        # step 1: initialize the three registers
        self.lfsr1 = LFSR(19, 8, [13, 16, 17, 18])
        self.lfsr2 = LFSR(22, 10, [20, 21])
        self.lfsr3 = LFSR(23, 10, [7, 20, 21, 22])

        # step 2: xor with session key
        for sk_bit in session_key:
            self.lfsr1.round_(0, sk_bit)
            self.lfsr2.round_(0, sk_bit)
            self.lfsr3.round_(0, sk_bit)

        # step 3: xor with frame counter
        for fc_bit in frame_counter:
            self.lfsr1.round_(0, fc_bit)
            self.lfsr2.round_(0, fc_bit)
            self.lfsr3.round_(0, fc_bit)

        # step 4: irregular clocking for 100 times
        for i in range(100):
            maj_bit = (self.lfsr1.reg[self.lfsr1.clocking] +
                       self.lfsr2.reg[self.lfsr2.clocking] +
                       self.lfsr3.reg[self.lfsr3.clocking]) // 2

            self.lfsr1.round_(1, maj_bit)
            self.lfsr2.round_(1, maj_bit)
            self.lfsr3.round_(1, maj_bit)


    def encrypt(self, fin, fout, plaintext_len):
        # xor the plaintext and key stream byte by byte
        for i in range(0, plaintext_len):
            self.key_stream_byte = []

            # step 5: generate plaintext_len bit key stream
            for _ in range(8):
                maj_bit = (self.lfsr1.reg[self.lfsr1.clocking] +
                           self.lfsr2.reg[self.lfsr2.clocking] +
                           self.lfsr3.reg[self.lfsr3.clocking]) >> 1

                self.key_stream_byte.append(self.lfsr1.reg[-1] ^
                                       self.lfsr2.reg[-1] ^
                                       self.lfsr3.reg[-1])

                self.lfsr1.round_(1, maj_bit)
                self.lfsr2.round_(1, maj_bit)
                self.lfsr3.round_(1, maj_bit)

            l1 = self.key_stream_byte
            l2 = map(int, bin(ord(fin.read(1)))[2:].zfill(8))
            l3 = map(int.__xor__, l1, l2)
            bn = functools.reduce(lambda x,y: x*2+y, l3)
            fout.write(bytearray([bn]))

            #if i % 64 == 0:
            #    print(i)



def main():

    if len(sys.argv) == 5:
        # use user's arguments

        # session_key
        try:
            session_key = int(sys.argv[1], 0)
        except:
            sys.stderr.write("Invalid Session Key input!")
            sys.exit(1)

        # frame_counter
        try:
            frame_counter = int(sys.argv[2], 0)
        except:
            sys.stderr.write("Invalid Frame Counter input!")
            sys.exit(1)

        # input_file
        try:
            if len(sys.argv[3]) > 255:
                sys.stderr.write("Input Filename too long!")
                sys.exit(1)

            input_file = sys.argv[3]

        except:
            sys.stderr.write("Invalid Input Filename!")
            sys.exit(1)

        # output_file
        try:
            if len(sys.argv[4]) > 255:
                sys.stderr.write("Output Filename too long!")
                sys.exit(1)

            output_file = sys.argv[4]

        except:

            sys.stderr.write("Invalid Input Filename!")
            sys.exit(1)

    elif len(sys.argv) == 1:
        # use default default configuration
        input_file    = "encrypt.mp3"
        output_file   = "decrypt.mp3"
        session_key   = 0x123456789ABCDEF0
        frame_counter = 0x00123456


    else:
        printf("Usage:./main [<Session Key> <Frame Counter> <Input Filename> <Output Filename>]")
        return -1


    try:
        fin = io.open(input_file, "rb")
        finb = io.BufferedReader(fin)
    except:
        sys.stderr.write("{}: No such file!".format(input_file))
        sys.exit(1)

    try:
        fout = io.open(output_file, "wb")
        foutb = io.BufferedWriter(fout)
    except:
        sys.stderr.write("{}: error while opening file to write!\n", output_file);
        sys.exit(1)

    # zfill and reverse the list
    session_key   = reversed(list(map(int, bin(session_key)[2:].zfill(64))))
    frame_counter = reversed(list(map(int, bin(frame_counter)[2:].zfill(22))))


    kerker_A5_1 = A5_1(session_key, frame_counter)

    input_file_len = os.stat(input_file).st_size

    kerker_A5_1.encrypt(finb, foutb, input_file_len)

    try:
        finb.close()
        foutb.close()
        fin.close()
        fout.close()
    except:
        sys.stderr.write("error on closing files!\n");
        sys.exit(1)

if __name__ == '__main__':
    main()


"""

Homework instuction

For students using languages other than C/C++, please follow this guide:
    1. Email TA, along with your preferred language, to request the permission to do so.
    2. Make sure your program can be executed the same as our skeleton.

        ./your_prog [<Session Key> <Frame Counter> <Input Filename> <Output Filename>]


Sample Input & Output

Sample 1.
    1. Download the original hw3.cpp file
    2. Run your program to encrypt hw3.cpp using following arguments
    ./your_prog 0x123456789abcdef 0x12345 hw3.cpp hw3.cpp.enc2
    3. The output hw3.cpp.enc2 should be identical to hw3.cpp.enc

Sample 2.
    1. Download encrypt.mp3
    2. Run your program without any argument
    ./your_prog
    3. The output decrypt.mp3 is a song you can find here
        https://archive.org/details/LastChristmas_614
"""
