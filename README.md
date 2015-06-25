SF Open Referral Source Data Library
====================================

##Installation

From the root of the repository, run the following:

    pip install virtualenv
    virtualenv venv
    source venv/bin/activate
    python setup.py develop
    pip install -r requirements.txt

##Usage

A `sforparser` script is provided for parsing data in a given format into JSON
matching the Open Referral spec.

###Examples

* sforparser -f apd data/apd/input.txt > data/apd/output.json

##Development

You can run tests with:

    py.test
