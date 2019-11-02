__author__ = "Isobel Ormiston <iormisto@cisco.com>"

# Run this script from the moonshine/tests directory with the following 
# command: python -m unittest moonshine_e2e_test.TestMoonshine

import unittest, subprocess, os

SUBTESTS_DIR = os.getcwd()

class TestMoonshine(unittest.TestCase):
    # This is a centralized test case, into which various easypy tests are 
    # passed to exercise a range of required test cases. 

    # Predefined logical testbed files and clean files are passed into these
    # easypy calls. These specify the host machine, where /nobackup/$USER is 
    # the default Moonshine host directory on that machine (see 
    # dyntopo/xrut/src/dyntopo/xrut/worker.py).


    def test_e2e(self):
        # Run tests on a Moonshine-Moonshine topology
        cmd = ['easypy', '{}/moonshine_test_job.py'.format(SUBTESTS_DIR)] 
        cmd.extend(['-logical_testbed_file', '{}/moonshine_moonshine_unicon_config.yaml'.format(SUBTESTS_DIR), 
                    '-clean_file', '{}/moonshine_moonshine_clean.yaml'.format(SUBTESTS_DIR), '-no_mail']) 

        print('Running the command {}'.format(cmd))

        output_1 = subprocess.check_output(cmd, universal_newlines=True) 
        print(output_1)
        output_1 = output_1.splitlines()


        # Test on an ios-Moonshine topology
        cmd = ['easypy', '{}/moonshine_test_job.py'.format(SUBTESTS_DIR)] 
        cmd.extend(['-logical_testbed_file', '{}/ios_moonshine_unicon_config.yaml'.format(SUBTESTS_DIR), 
                    '-clean_file', '{}/ios_moonshine_clean.yaml'.format(SUBTESTS_DIR), '-no_mail']) 

        print('Running the command {}'.format(cmd))

        output_2 = subprocess.check_output(cmd, universal_newlines=True) 
        print(output_2)
        output_2 = output_2.splitlines()

        expected = '''
__task1: config_test
`-- commonSetup                                                           PASSED
    `-- connect_and_test                                                  PASSED
__task2: standalone_ping_test
`-- commonSetup                                                           PASSED
    `-- connect                                                           PASSED
'''.splitlines()     

        for i in expected:
            self.assertTrue(any([i in j for j in output_1]))
            self.assertTrue(any([i in j for j in output_2]))

        print("Moonshine end-to-end test passed.")



if __name__ == '__main__':
    unittest.main()
