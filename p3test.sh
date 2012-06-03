#!/usr/bin/env bash

set -e
DIR=".tox/python3"

init() {

    mkdir -p "$DIR"
    virtualenv -qp `which python3` "$DIR"
    source "$DIR/bin/activate"
    easy_install cram nose
    deactivate
}

main() {

    source "$DIR/bin/activate"
    rm -rf build/ dist/
    python setup.py -q install
    cp -r specs/ "$DIR/specs"
    2to3 -wn --no-diffs "$DIR/specs" 2>/dev/null
    (cd $DIR && nosetests specs/)
    cram specs/
    deactivate
}


if [ ! -d "$DIR" ]; then
    init
fi

main
