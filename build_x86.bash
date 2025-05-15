
echo "START====platform=amd64======"
echo "START====platform=amd64======"
echo "START====platform=amd64======"
echo "START====platform=amd64======"
docker system prune
docker build --no-cache --platform=linux/amd64 -t redline_x86 .
echo "END==========="
echo "END==========="
echo "END==========="
echo "END==========="
docker images 
echo "==========="
echo "==========="
echo "==========="
echo "==========="
echo "==========="
