# NAO_ObjectInteraction
A program for the NAO robot to interact with a red ball of any diameter.



Name: Benjamin Hodgson

Used modules (should have all of these already):

    import argparse
    import time
    import math
    from naoqi import ALBroker, ALModule, ALProxy



What does this program do?

    This program allows the NAO robot to interact with a red ball, in an open environment,
    with a human observer. The robot will first look for the ball, move to, and grab the ball if found,
    and eventually return the ball.

How to run:
    
    note: This program will set up the robot connection for you. The terminal has a small
          amount of input required so that the robot can function properly.

    1. Call the program in a terminal.
    2. To automate the process, type and enter 'find_ball' in the terminal- other functions
       will be called following find_balls completion.
    3. You can enter the balls diameter in the terminal, ensure this is accurate, the default
       is 0.07m.
    4. If the ball is closer, the robot is much more likely to find it, and be able to
       get to it.
    5. All other functions can be called from the terminal- after the current function has
       has been completed.
    6. Function list: 'find_ball', 'take_ball', 'give_ball'
    7. To cancel a function, touch the middle tactile on the head of the NAO robot.
    8. Note that if the robot is unsuccessful it will cancel the action eventually
       anyway.
    
