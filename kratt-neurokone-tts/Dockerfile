FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /opt/neurokone

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --timeout 120 --retries 10 -r /tmp/requirements.txt

COPY wyoming_neurokone.py ./
COPY run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 10301
CMD ["/run.sh"]
