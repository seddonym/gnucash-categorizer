Gnucash Categorizer
========================

(Under construction.)

Command line tool to move GnuCash transactions into the correct accounts,
based on their descriptions.
  

Installation
------------
    
   mkvirtualenv -ppython3 gnucash-categorizer
   pip install git+git@github.com:seddonym/gnucash-categorizer.git
   

Usage
-----

First, create a config.yaml file.

    workon gnucash-categorizer
    gnucash-categorize config.yaml accounts.gnucash

Local development
-----------------
    
    git clone git@github.com:seddonym/gnucash-categorizer.git
    cd gnucash-categorizer
    mkvirtualenv -ppython3 gnucash-categorizer
    pip install -e .


You may need to install this::

    sudo apt-get install libdbd-sqlite3
