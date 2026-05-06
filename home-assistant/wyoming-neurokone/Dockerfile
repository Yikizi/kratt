FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wyoming_neurokone.py .
EXPOSE 10301
ENTRYPOINT ["python", "wyoming_neurokone.py"]
CMD ["--uri", "tcp://0.0.0.0:10301", "--voice", "mari"]
