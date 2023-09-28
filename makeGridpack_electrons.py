#! /usr/bin/env python

# Official twiki:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/QuickGuideMadGraph5aMCatNLO
import os,sys
import argparse

def replace_gridpack_generation():
    '''
        official gridpack_generation.sh load extra models
        from central afs directory. One needs to write 
        permission to put his/her UFO there. This is of
        course doable, by submitting request:
        https://twiki.cern.ch/twiki/bin/view/CMS/GeneratorWebRepo

        But for private production and avoid such hassle,
        the workaround is download it from a controllable place.
        The benefit is to keep most other part intact, while 
        minimum changes if official production is desired.
    '''
    cwd = os.getcwd()
    os.chdir( cwd+'/../' )
    if not os.path.isfile('gridpack_generation.sh'):
        sys.exit('gridpack_generation.sh Not exist!! exiting..')
    if not os.path.isfile('gridpack_generation.sh.bkp'):
        # backing up
        cmd = 'cp gridpack_generation.sh gridpack_generation.sh.bkp'
        os.system(cmd)

        replaceWith = 'wget --no-check-certificate https://www.classe.cornell.edu/~skb93/iDMe/iDM_MG5_models/$model'
        toBeReplaced = 'wget --no-check-certificate https://cms-project-generators.web.cern.ch/cms-project-generators/$model'
        cmd = 'sed -i "s#%s#%s#g" gridpack_generation.sh' % (toBeReplaced, replaceWith)
        print cmd
        os.system(cmd)
    else:
        print 'gridpack_generation.sh already replaced.'
    os.chdir(cwd)

def format_template(template, paramMap):
    for p in paramMap:
        template = template.replace(p, paramMap[p])
    return template

def stringfy_friendly(num):
    '''
        0.4 -> '0p4'
        125 -> '125'
    '''
    if isinstance(num, int):
        return str(num)
    elif isinstance(num, float):
        if int(num*100) > 0:
            num = round(num, 2)
            return str(num).replace('.', 'p') if '.' in str(num) else str(num)
        else:
            num = '%.2e' % num
            return num.replace('.', 'p')
    else:
        raise ValueError("{0} is not a number!".format(num))

def create_parametrized_cards(tempDir, tag, params):
    '''
        copying template cards folder into MadGraph5_aMCatNLO/cards
        with parametrization
    '''
    cwd = os.getcwd()
    os.chdir('cards')
    if os.path.isdir(tag):
        os.system('rm -rf {0}'.format(tag))
    os.system('cp -r {0} {1}'.format(tempDir, tag))
    os.chdir(tag)
    for f in os.listdir(os.getcwd()):
        if 'custom' in f:
            program_customizecards(f, params)
            target = tag+'_customizecards.dat'
        elif 'proc' in f:
            program_proccard(f, tag)
            target = tag+'_proc_card.dat'
        elif 'extramodels' in f:
            target = tag+'_extramodels.dat'
        elif 'run_card' in f:
            target = tag+'_run_card.dat'
        elif 'param_card' in f:
            target = tag+'_param_card.dat'
        else:
            sys.exit('unknown card exist! --> {0}'.format(f))
        cmd = 'mv {0} {1}'.format(f, target)
        os.system(cmd)

    os.chdir(cwd)
    if os.path.isdir('../cards/{0}'.format(tag)):
        os.system('rm -rf ../cards/{0}'.format(tag))
    os.system('cp -r cards/{0} ../cards/'.format(tag))

def program_customizecards(f, params):
    for p in params:
        cmd = 'sed -i "s#%s#%s#g" %s' % (p, str(params[p]), f)
        os.system(cmd)

def program_proccard(f, tag):
    inf = open(f, 'r')
    otf = open(f+'.tmp', 'w')
    for line in inf:
        if line.split()[0] == 'output':
            line = ' '.join([line.split()[0], tag, line.split()[-1]])
        otf.write(line)
    inf.close()
    otf.close()
    os.system('mv {0} {1}'.format(f+'.tmp', f))

def run_gridpack_generation(tag):
    '''
    ./gridpack_generation.sh <name of process card without _proc_card.dat>
    <folder containing cards relative to current location>
    '''
    cwd = os.getcwd()
    os.chdir(cwd+'/../')
    if os.path.isdir(tag):
        print "Remenant exists! Cleaning.. ",
        os.system('rm -rf '+tag)
        print "Cleaned!"
    cmd = './gridpack_generation.sh {0} cards/{0} local ALL slc7_amd64_gcc820 CMSSW_10_6_28'.format(tag)
    #cmd = './gridpack_generation.sh {0} cards/{0} local ALL slc7_amd64_gcc630 CMSSW_9_3_16'.format(tag)
    print cmd
    os.system(cmd)
    #cmd = 'mv %s_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz %s.tar.xz' % (tag, tag)
    #print cmd
    #os.system(cmd)
    # clean working directory, it's useless
    os.system('rm -rf %s &' % tag)
    os.chdir(cwd)

def run_condor(tag):
    cwd = os.getcwd()
    if os.path.isdir('condor/{0}'.format(tag)):
        os.system('rm -rf condor/{0}'.format(tag))
        os.system('mkdir condor/{0}'.format(tag))
    else:
        os.system('mkdir condor/{0}'.format(tag))
    os.system('cp ../gridpack_generation.sh condor/{0}'.format(tag))
    os.system('mkdir condor/{0}/cards'.format(tag))
    os.system('cp -r cards/{0} condor/{0}/cards/'.format(tag))
    os.chdir('condor/{0}/'.format(tag))
    os.system('tar -czf ../{0}.tar.gz *'.format(tag))
    os.chdir(cwd)

    condor_cmd = "condor_submit condorTemplate.jdl"
    condor_cmd += " -append \"Arguments = {0}\"".format(tag)
    condor_cmd += " -append \"transfer_input_files = condor/{0}.tar.gz\"".format(tag)
    condor_cmd += " -append \"output = condor/{0}/\$(Cluster)_\$(Process).out\"".format(tag)
    condor_cmd += " -append \"error = condor/{0}/\\$(Cluster)_\$(Process).err\"".format(tag)
    condor_cmd += " -append \"log = condor/{0}/\\$(Cluster)_\\$(Process).log\"".format(tag)

    os.system(condor_cmd)

def lsf_submit(tag):
    '''
    ./submit_gridpack_generation.sh <memoryInMBytes> <diskInMBytes>
    <queueForMasterJob> <name of process card without _proc_card.dat> <folder
    containing cards relative to current location> <queue>
    '''
    cwd = os.getcwd()
    os.chdir(cwd+'/../')
    #cmd = './submit_gridpack_generation.sh 15000 15000 2nw {0} cards/{0} 8nh'.format(tag)
    cmd = './submit_gridpack_generation.sh 15000 15000 8nh {0} cards/{0} 8nh'.format(tag)
    os.system(cmd)
    cmd = 'mv %s_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz GridPacker/GridPacks/%s.tar.xz' % (tag, tag)
    os.chdir(cwd)

def condor_submit(tag):
    '''
    ./submit_condor_gridpack_generation.sh <name of process card without _proc_card.dat>
    <folder containing cards relative to current location> <scram_arch> <cmssw_version>
    '''
    cwd = os.getcwd()
    os.chdir(cwd+'/../')
    cmd = './submit_condor_gridpack_generation.sh {0} cards/{0}'.format(tag)
    os.system(cmd)
    cmd = 'mv %s_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz GridPacker/GridPacks/%s.tar.xz' % (tag, tag)
    os.chdir(cwd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--m1', type=float, help='M1', required=True)
    parser.add_argument('--delta', type=float, help='Mass splitting', required=True)
    parser.add_argument('--onejet', type=str, help='1jet or not, default is False', default='False')
    parser.add_argument('--mA_over_m1', type=float, help="M(A')/M1, default is 3", default=3.)

    args = parser.parse_args()

    oneJet = False

    if eval(args.onejet) == True:
        oneJet = True

    replace_gridpack_generation()

    template = 'iDMe_Mchi-XMASS_dMchi-XHS_mZDinput-MED_ctau-DLENGTH_1or2jets_icckw1_drjj0_xptj80_xqcut20'
    if oneJet:
        template = 'iDMe_Mchi-XMASS_dMchi-XHS_mZDinput-MED_ctau-DLENGTH_1jet_icckw1_drjj0_xptj80_xqcut20'

    # Parsing arguments
    m1 = args.m1
    delta = args.delta
    m2 = m1*(1+delta)
    mchi = (m1+m2)/2
    dmchi = m2-m1
    med = args.mA_over_m1 * m1
    
    print 'Preparing local submission for mass parameters m1 = %s GeV, m2 = %s GeV:' % (m1, m2)
    ctau = 0 #placeholder, will be changed when PYTHIA is run
    print '\tMass average: mchi = %.2f \n\tMass difference: dmchi = %.2f \n\tDark photon mass: med = %.2f' % (mchi, dmchi, med)

    # format gridpack name template with specific parameters
    rawParams = {'XMASS': mchi, 'MED': med, 'XHS': dmchi} #'EPSILON': epsilon}
    tagParams = {'XMASS': stringfy_friendly(mchi), 'MED': stringfy_friendly(med), 'XHS': stringfy_friendly(dmchi), 'DLENGTH': stringfy_friendly(ctau)}
    tag = format_template(template, tagParams)

    # create the madgraph cards with specified masses 
    tempDir = 'iDMe_generic'
    if oneJet:
        tempDir = 'iDMe_generic_1jet'
    create_parametrized_cards(tempDir, tag, rawParams)
    os.system('ls -alrth ../cards')
    run_gridpack_generation(tag)
    #run_condor(tag)
    #lsf_submit(tag)
    #condor_submit(tag)

