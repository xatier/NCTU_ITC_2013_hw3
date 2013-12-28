Intro to cryptography homework 3
================================

## Implement a A5/1 cipher

# for TA

    # prepare hw3.cpp under the same directory of hw3.py
    # this will decode hw3.cpp and output hw3.cpp.enc2
    ./hw3.py 0x123456789abcdef 0x12345 hw3.cpp hw3.cpp.enc2
    
    # prepare encrypt.mp3 under the same directory of hw3.cp
    # this will decode the mp3, it will take around 90 seconds
    ./hw3.py

----


## Algorithm

The algorithm is based on [this video](https://www.youtube.com/watch?v=LgZAI3DdUA4)

- Note that there's some incorrect around 01:19 and 01:57

    The first bit of LFSR 3
    
        cycle 10 -> 11
        cycle 2->3

- Typo in step 5 introduction

    inicialization -> initialization

## PyPy

Because use the CPython interpreter is very slow, I use PyPy instead.

PyPy3 is slower than PyPy2, so I modified my program to Python2 :(
