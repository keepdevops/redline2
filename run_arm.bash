

echo "RUN====ARM-OSX=============="
echo "RUN====ARM-OSX=============="
echo "RUN====ARM-OSX=============="
echo "RUN====ARM-OSX=============="
echo "RUN====ARM-OSX=============="



# xhost +local:
xhost +
docker run --rm \
  -e DISPLAY=host.docker.internal:0 \
  -v "$(pwd):/app" \
  -v $(pwd)/data:/app/data \
  redline_arm python3 /app/data_module.py


xhost -

echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="

