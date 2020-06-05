DEST='/vol/bitbucket/rh2515/MRI_Crohns'
for a in 'A' 'I'
do
  for ext in '.nii.gz' '.nii'
  do
    for i in {1..100}
    do
      BASE=${DEST}/${a}/${a}${i}

      mv ${BASE}\ T2\ Ax${ext}              ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ T2\ Axial${ext}           ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ t2\ ax${ext}              ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ T2\ axial${ext}           ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ T2\ AX${ext}              ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ T2\ axial\ HASTE${ext}    ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ T2\ HASTE\ axial${ext}    ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ Ax\ T2${ext}              ${BASE}\ Axial\ T2${ext}
      mv ${BASE}\ axial\ HASTE${ext}        ${BASE}\ Axial\ T2${ext}
    done
  done
done
