#!/usr/bin/env python3

import sys
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
    def __init__(self, session_key, frame_counter, plaintext_len):
        self.key_stream = []

        # step 1: initialize the three registers
        lfsr1 = LFSR(19, 8, [13, 16, 17, 18])
        lfsr2 = LFSR(22, 10, [20, 21])
        lfsr3 = LFSR(23, 10, [7, 20, 21, 22])

        # step 2: xor with session key
        for sk_bit in session_key:
            lfsr1.round_(0, sk_bit)
            lfsr2.round_(0, sk_bit)
            lfsr3.round_(0, sk_bit)

        # step 3: xor with frame counter
        for fc_bit in frame_counter:
            lfsr1.round_(0, fc_bit)
            lfsr2.round_(0, fc_bit)
            lfsr3.round_(0, fc_bit)

        # XXX: cause of the wrong part in video
        lfsr3.reg = [0,0,0,0,  1,0,1,1,  0,0,0,1, 1,0,0,1,  1,0,1,0,  0,1,0]

        # step 4: irregular clocking for 100 times
        for i in range(100):
            maj_bit = (lfsr1.reg[lfsr1.clocking] +
                       lfsr2.reg[lfsr2.clocking] +
                       lfsr3.reg[lfsr3.clocking]) // 2

            lfsr1.round_(1, maj_bit)
            lfsr2.round_(1, maj_bit)
            lfsr3.round_(1, maj_bit)


        # step 5: generate plaintext_len bit key stream
        for i in range(plaintext_len):
            maj_bit = (lfsr1.reg[lfsr1.clocking] +
                       lfsr2.reg[lfsr2.clocking] +
                       lfsr3.reg[lfsr3.clocking]) // 2

            self.key_stream.append(lfsr1.reg[-1] ^
                                   lfsr2.reg[-1] ^
                                   lfsr3.reg[-1])
            lfsr1.round_(1, maj_bit)
            lfsr2.round_(1, maj_bit)
            lfsr3.round_(1, maj_bit)

        #lfsr1.print_()
        #lfsr2.print_()
        #lfsr3.print_()
        #print(self.key_stream)

    def encrypt(self):
        # xor the plaintext and key stream
        pass

    def decrypt(self):
        # xor the ciphertext and key stream
        pass


def main():
    # default configuration
    input_file    = "encrypt.mp3"
    output_file   = "decrypt.mp3"
    session_key   = 0x123456789ABCDEF0
    frame_counter = 0x00123456

    session_key   = [ int(b) for b in bin(session_key)[2:] ]
    frame_counter = [ int(b) for b in bin(frame_counter)[2:] ]

    # session_key = [0,1,0,0,  1,1,1,0,  0,0,1,0,  1,1,1,1,
    #                0,1,0,0,  1,1,0,1,  0,1,1,1,  1,1,0,0,
    #                0,0,0,1,  1,1,1,0,  1,0,1,1,  1,0,0,0,
    #                1,0,0,0,  1,0,1,1,  0,0,1,1,  1,0,1,0]

    # frame_counter = [    1,1, 1,0,1,0, 1,0,1,1,
    #                  0,0,1,1, 1,1,0,0, 1,0,1,1]


    if len(sys.argv) == 5:
        # use user's arguments
        # session_key
        try:
            session_key = sys.argv[1]
        except:
            sys.stderr.write("Invalid Session Key input!")
            sys.exit(1)

        # frame_counter
        try:
            frame_counter = sys.argv[2]
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

            output_file = sys.argv[3]
        except:

            sys.stderr.write("Invalid Input Filename!")
            sys.exit(1)

    elif len(sys.argv) == 1:
        # use default arguments

    else:
        printf("Usage:./main [<Session Key> <Frame Counter> <Input Filename> <Output Filename>]")
        return -1

    kerker_A5_1 = A5_1(session_key, frame_counter, 228)


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
