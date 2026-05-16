# Local TartuNLP Estonian TTS for Home Assistant/Wyoming.
#
# This deliberately uses the local worker image instead of calling the public
# Neurokõne API. Upstream/provenance:
#   https://github.com/TartuNLP/text-to-speech-worker
#   release/image: v3.1.0 / ghcr.io/tartunlp/text-to-speech-worker:3.1.0
FROM ghcr.io/tartunlp/text-to-speech-worker:3.1.0

USER root
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/home/app/.local/lib/python3.10/site-packages

RUN python3 -m pip install --no-cache-dir "wyoming>=1.5.0"

WORKDIR /opt/kratt
COPY wyoming_tartunlp_local.py ./
COPY run.sh /run.sh
RUN chmod a+x /run.sh && mkdir -p /data /opt/kratt

EXPOSE 10301
ENTRYPOINT []
CMD ["/run.sh"]
