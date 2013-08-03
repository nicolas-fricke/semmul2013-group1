#!/bin/bash

EXPECTED_ARGS=3
E_BADARGS=65

if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Usage: `basename $0` DB_FILE OUTPUT_FILE TABLE_TO_EXPORT"
  exit $E_BADARGS
fi

sqlite3 $1 <<!
.headers on
.mode csv
.output $2
select * from $3;
!
