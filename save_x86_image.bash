
echo "SAVE redline_x86 DOCKER IMAGE================"
echo "SAVE redline_x86 DOCKER IMAGE================"
echo "SAVE redline_x86 DOCKER IMAGE================"
echo "SAVE redline_x86 DOCKER IMAGE================"
echo "-1----------------"
sleep 1
ls -lrt ~/DOCKER_IMAGES
echo "-2----------------"
sleep 1
docker save -o ~/DOCKER_IMAGES/redline_x86.tar redline_x86:latest
echo "-3----------------"
sleep 1
chmod ugo+rwx ~/DOCKER_IMAGES/redline_x86.tar
echo "-4----------------"
sleep 1
ls -lrt ~/DOCKER_IMAGES
echo "-5----------------"
sleep 1
ls -lrt /Volumes/64GB-TEMP
echo "-6----------------"
sleep 1
cp ~/DOCKER_IMAGES/redline_x86.tar /Volumes/64GB-TEMP/.
echo "-7----------------"
sleep 1
ls -lrt /Volumes/64GB-TEMP
echo "-8----------------"
cp * /Volumes/64GB-TEMP/.
sleep 1
echo "-9----------------"
ls -lrt /Volumes/64GB-TEMP
echo "DONE ================"
echo "DONE ================"
echo "DONE ================"
echo "DONE ================"
echo "DONE ================"

