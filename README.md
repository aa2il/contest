# Cabrillo log conversion and Contest Scoring

Command-line program to convert adif log for a contest into cabrillo format and compute claimed score.

# Installation under Linux:

1) Uses python3 
2) Clone gitub contest, libs and data repositories
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/contest
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data
3) Install packages needed for contest:
   - cd ~/Python/contest
   - pip3 install -r requirements.txt
4) Make sure its executable:
   - chmod +x contest.py start start_cw
5) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"
6) To run contest, take a look at "score" to see how to set the various args.

# Installation under Mini-conda:

0) Good video:  https://www.youtube.com/watch?v=23aQdrS58e0&t=552s

1) Point browser to https://docs.conda.io/en/latest/miniconda.html
2) Download and install latest & greatest Mini-conda for your particular OS:
   - I used the bash installer for linux
   - As of July 2023: Conda 23.5.2 Python 3.11.3 released July 13, 2023
   - cd ~/Downloads
   - bash Miniconda3-latest-Linux-x86_64.sh
   - Follow the prompts

   - If you'd prefer that conda's base environment not be activated on startup, 
      set the auto_activate_base parameter to false: 

      conda config --set auto_activate_base false

   - To get it to work under tcsh:
       - bash
       - conda init tcsh
       - This creates ~/.tcshrc - move its contents to .cshrc if need be
       - relaunch tcsh and all should be fine!
       - Test with:
           - conda list

3) Create a working enviroment for ham radio stuff:
   - !!! THERE IS A BUG IN re in python 3.11 - need to use 3.10 !!!
   - conda create --name aa2il python=3.10

   - To activate this environment, use:
       - conda activate aa2il
   - To deactivate an active environment, use:
       - conda deactivate

   - conda env list
   - conda activate aa2il

4) Clone gitub contest, libs and data repositories:
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/contest
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data

5) Install packages needed by contest:
   - cd ~/Python/contest
   - pip3 install -r requirements.txt

6) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"

7) To run contest, take a look at "score" to see how to set the various args.

8) Known issues using this (as of July 2023):
   - Fonts look awful - probably need to install these also

# Installation for Windoz:

1) Best bet is to use mini-conda and follow the instructions above.
2) If you want/need a binary, email me.
