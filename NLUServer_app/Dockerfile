FROM python:3.9
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "./src/main.py" ] # ここには適切なpythonスクリプトのパスを記述してください
