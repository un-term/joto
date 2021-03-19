#!/bin/sh
sqlite3 -header -csv joto.db "select * from joto;" > joto.csv
