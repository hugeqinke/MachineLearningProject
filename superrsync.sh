#!/bin/bash

for i in `seq $1 $2`
do
    rsync -avz --exclude "text-versions" --include '*/' --include 'data.json' --delete --delete-excluded --exclude '*' govtrack.us::govtrackdata/congress/$i/bills ./$i    
done
