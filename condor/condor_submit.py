import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--m1', type=float, help='M1', required=True)
parser.add_argument('--delta', type=float, help='Mass splitting', required=True)
parser.add_argument('--onejet', type=str, help='1jet or not, default is False', default='False')
parser.add_argument('--mA_over_m1', type=float, help="M(A')/M1, default is 3", default=3.)

args = parser.parse_args()

m1 = args.m1
delta = args.delta
onejet = args.onejet
mA_over_m1 = args.mA_over_m1

arg_cmd = f'Arguments = {m1} {delta} {onejet} {mA_over_m1}'

currentDir = os.getcwd()

os.chdir('../../../../')
os.system('tar -czf submit.tar.gz *')

os.chdir(currentDir)
os.system('mv ../../../../submit.tar.gz .')

logDir = f'log_m1_{m1}_dMchi_{delta}_onejet_{onejet}_mA_over_m1_{mA_over_m1}'
if not os.path.isdir(logDir):
    os.makedirs(logDir)

condor_cmd = 'condor_submit condorTemplate.jdl'
condor_cmd += f' -append \"{arg_cmd}\"'
condor_cmd += ' -append \"transfer_input_files = submit.tar.gz\"'
condor_cmd += f' -append \"output = {logDir}/\$(Cluster)_\$(Process).out\"'
condor_cmd += f' -append \"error = {logDir}/\$(Cluster)_\$(Process).err\"'
condor_cmd += f' -append \"log = {logDir}/\$(Cluster)_\$(Process).log\"'
condor_cmd += ' -append \"Queue 1\"'

print(condor_cmd)
os.system(condor_cmd)
