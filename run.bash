

echo "RUN=================="
echo "RUN=================="
echo "RUN=================="
echo "RUN=================="
echo "RUN=================="



xhost +
docker run --rm \
  -e DISPLAY=host.docker.internal:0 \
  -v "$(pwd):/app" \
  redline python3 /app/data_module.py


xhost -

echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="

