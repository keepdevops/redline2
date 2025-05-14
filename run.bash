

echo "RUN=================="
echo "RUN=================="
echo "RUN=================="
echo "RUN=================="
echo "RUN=================="
#
#  docker run --rm -v "$(pwd)/data:/app/data" -v "$(pwd)/redline_data.duckdb:/app/redline_data.duckdb" \\n  redline python3 -m data_module --task=load\n
#
docker run --rm redline python3 data_module.py 
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="
echo "DONE=================="

