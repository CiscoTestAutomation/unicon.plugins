import os
import sys
from ats.easypy import run

def main():
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_testscript = os.path.join(test_path, 'tests', 'config_test.py')
    ping_testscript = os.path.join(test_path, 'tests', 'standalone_ping_test.py')

    run(testscript=config_testscript , uut1_name='r1',
        uut2_name='r2', uut1_if_name='if1.1', uut2_if_name='if2.1')
    run(testscript=ping_testscript , uut1_name='r1',
        uut2_name='r2', uut1_if_name='if1.1', uut2_if_name='if2.1')
