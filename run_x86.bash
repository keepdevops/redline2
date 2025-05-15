

echo "RUN===x86==============="
echo "RUN===x86==============="
echo "RUN===x86==============="
echo "RUN===x86==============="
echo "Docker Desktop -> enable QEMU"
echo "Docker Desktop -> enable QEMU"
echo "Docker Desktop -> enable QEMU"



# xhost +local:
xhost +
docker run --rm \
  --platform=linux/amd64 \
  -e POLARS_SKIP_CPU_CHECK=1 \
  -e DISPLAY=host.docker.internal:0 \
  -v "$(pwd):/app" \
  -v $(pwd)/data:/app/data \
  redline_x86 python3 /app/data_module.py

xhost -

echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="

