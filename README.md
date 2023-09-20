# iDMeGridpacker
This repository contains a basic script to generate gridpacks using the tools from the [genproductions](https://github.com/cms-sw/genproductions/tree/master) repository.

## Instructions
To set up gridpack generation, first clone the `mg265UL` branch of the `genproductions` repository:
```bash
git clone -b mg265UL --single-branch https://github.com/cms-sw/genproductions.git
```
Next, move to the MadGraph area and clone *this* repository:
```bash
cd genproductions/bin/MadGraph5_aMCatNLO/
git clone https://github.com/SamBT/iDMeGridpacker.git
cd iDMeGridpacker
```

To generate a gridpack locally (I haven't written a way to do this on condor yet, but I should..), run the following command:
```bash
python makeGridpack.py M1 DELTA [1jet]
```
where M1 is the lighter DM mass in GeV, DELTA is the mass splitting as a fraction of M1 (e.g. use 0.1 for a 10% splitting), and the optional third argument `1jet` instructs MadGraph to only consider diagrams with 1 jet. For now, **the `1jet` mode is preferred** since it takes a much longer time to generate gridpacks with the additional option of 2 jets in the final state. We do not specify the lifetime in generating the gridpacks, as the decay is handled by Pythia.

This script will create a gridpack in the parent directory titled `iDMe_Mchi-XMASS_dMchi-XHS_mZDinput-MED_ctau-DLENGTH_1jet_icckw1_drjj0_xptj80_xqcut20` for the `1jet` option, or `iDMe_Mchi-XMASS_dMchi-XHS_mZDinput-MED_ctau-DLENGTH_1or2jets_icckw1_drjj0_xptj80_xqcut20` for the multijet option. The `XMASS` field will be filled in with $m_\chi = (m_1+m_2)/2$, `XHS` will be filled by $\Delta m_\chi = \Delta \times m_1$, `MED` will be filled with the default dark photon mass $m_{A^\prime} = 3m_1$, and DLENGTH will be filled with a dummy value of 0. Note that you will have to change the code in the gridpack-making script if you want to explore dark photon mass points that are not fixed to $3m_1$.

## Storing gridpacks on eos
Existing gridpacks are stored on eos at `/store/group/lpcmetx/iDMe/gridpacks/`. Please upload any new gridpacks you make! (This is also a good way to make sure you have write access to the `lpcmetx` area)