FOLDS=$3

BASE="/vol/project/2019/545/g1954502/softwareengineering_group_project/" # this has to be changed to local directory
RECORDS="CrohnsDisease/tfrecords/axial_t2_only" # to train the tfrecords have to be made from the original data
TIMESTAMP=`date +%Y-%m-%d_%H:%M:%S`


echo "Running ${@} fold(s)"

for fold in ${@}
do
  python3 run.py \
  Crohns_MRI \
  ${BASE} \
  ${BASE}/${RECORDS}_train_fold${fold}.tfrecords \
  ${BASE}/${RECORDS}_test_fold${fold}.tfrecords \
  -record_shape 37,99,99 \
  -feature_shape 31,87,87 \
  -at=1 \
  -f=${fold} \
  -bS=32 \
  -lD=log_attention/${TIMESTAMP}/ \
  -nB=1200 \
  -mode="train"
done
echo "---------------"
