#!/bin/bash

# OSRMのデータセットアップスクリプト

# OSRM_serverディレクトリのdataサブディレクトリにデータを保存する
mkdir -p OSRM_server/data

# OpenStreetMapのデータのダウンロード
if [ ! -f OSRM_server/data/japan-latest.osm.pbf ]; then
  echo "Downloading OSM data for Japan..."
  wget -P OSRM_server/data https://download.geofabrik.de/asia/japan-latest.osm.pbf
else
  echo "OSM data for Japan already exists. Skipping download."
fi

# データの抽出
echo "Extracting OSM data for OSRM..."
docker run --platform linux/amd64 -t -v "${PWD}/OSRM_server/data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/japan-latest.osm.pbf

# データのパーティション
echo "Partitioning the extracted data..."
docker run --platform linux/amd64 -t -v "${PWD}/OSRM_server/data:/data" osrm/osrm-backend osrm-partition /data/japan-latest.osrm

# データのカスタマイズ
echo "Customizing the partitioned data..."
docker run --platform linux/amd64 -t -v "${PWD}/OSRM_server/data:/data" osrm/osrm-backend osrm-customize /data/japan-latest.osrm

echo "Setup complete. You can now run OSRM with Docker Compose."
