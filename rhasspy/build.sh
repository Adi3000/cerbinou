#!/bin/bash
source .env

COPY='rsync -a'
cd ${BASE_DIR}
rm -rf ${DOWNLOAD_DIR}
rm -rf ${BUILD_DIR}
rm -rf ${APP_DIR}
#pip uninstall numpy scipy  -y

mkdir -p ${BUILD_DIR}
mkdir -p ${APP_DIR}
mkdir -p ${DOWNLOAD_DIR}
mkdir -p ${BUILD_DIR}/rhasspy-snips-nlu/etc
mkdir -p ${BUILD_DIR}/scripts
mkdir -p ${APP_DIR}/.venv
mkdir -p ${BUILD_DIR}/rhasspy-wake-raven/rhasspywake_raven
$COPY download/shared/ ${DOWNLOAD_DIR}/shared/
$COPY download/${TARGETARCH}${TARGETVARIANT}/ ${DOWNLOAD_DIR}/${TARGETARCH}${TARGETVARIANT}/


# Copy Rhasspy module requirements
$COPY rhasspy-server-hermes/requirements.txt ${BUILD_DIR}/rhasspy-server-hermes/
$COPY rhasspy-wake-snowboy-hermes/requirements.txt ${BUILD_DIR}/rhasspy-wake-snowboy-hermes/
$COPY rhasspy-wake-porcupine-hermes/requirements.txt ${BUILD_DIR}/rhasspy-wake-porcupine-hermes/
$COPY rhasspy-wake-precise-hermes/requirements.txt ${BUILD_DIR}/rhasspy-wake-precise-hermes/
$COPY rhasspy-profile/requirements.txt ${BUILD_DIR}/rhasspy-profile/
$COPY rhasspy-asr/requirements.txt ${BUILD_DIR}/rhasspy-asr/
$COPY rhasspy-asr-deepspeech/requirements.txt ${BUILD_DIR}/rhasspy-asr-deepspeech/
$COPY rhasspy-asr-deepspeech-hermes/requirements.txt ${BUILD_DIR}/rhasspy-asr-deepspeech-hermes/
$COPY rhasspy-asr-pocketsphinx/requirements.txt ${BUILD_DIR}/rhasspy-asr-pocketsphinx/
$COPY rhasspy-asr-pocketsphinx-hermes/requirements.txt ${BUILD_DIR}/rhasspy-asr-pocketsphinx-hermes/
$COPY rhasspy-asr-kaldi/requirements.txt ${BUILD_DIR}/rhasspy-asr-kaldi/
$COPY rhasspy-asr-kaldi-hermes/requirements.txt ${BUILD_DIR}/rhasspy-asr-kaldi-hermes/
$COPY rhasspy-asr-vosk-hermes/requirements.txt ${BUILD_DIR}/rhasspy-asr-vosk-hermes/
$COPY rhasspy-dialogue-hermes/requirements.txt ${BUILD_DIR}/rhasspy-dialogue-hermes/
$COPY rhasspy-fuzzywuzzy/requirements.txt ${BUILD_DIR}/rhasspy-fuzzywuzzy/
$COPY rhasspy-fuzzywuzzy-hermes/requirements.txt ${BUILD_DIR}/rhasspy-fuzzywuzzy-hermes/
$COPY rhasspy-hermes/requirements.txt ${BUILD_DIR}/rhasspy-hermes/
$COPY rhasspy-homeassistant-hermes/requirements.txt ${BUILD_DIR}/rhasspy-homeassistant-hermes/
$COPY rhasspy-microphone-cli-hermes/requirements.txt ${BUILD_DIR}/rhasspy-microphone-cli-hermes/
$COPY rhasspy-microphone-pyaudio-hermes/requirements.txt ${BUILD_DIR}/rhasspy-microphone-pyaudio-hermes/
$COPY rhasspy-nlu/requirements.txt ${BUILD_DIR}/rhasspy-nlu/
$COPY rhasspy-nlu-hermes/requirements.txt ${BUILD_DIR}/rhasspy-nlu-hermes/
$COPY rhasspy-rasa-nlu-hermes/requirements.txt ${BUILD_DIR}/rhasspy-rasa-nlu-hermes/
$COPY rhasspy-remote-http-hermes/requirements.txt ${BUILD_DIR}/rhasspy-remote-http-hermes/
$COPY rhasspy-silence/requirements.txt ${BUILD_DIR}/rhasspy-silence/
$COPY rhasspy-snips-nlu/requirements.txt ${BUILD_DIR}/rhasspy-snips-nlu/
$COPY rhasspy-snips-nlu/etc/languages/ ${BUILD_DIR}/rhasspy-snips-nlu/etc/languages/
$COPY rhasspy-snips-nlu-hermes/requirements.txt ${BUILD_DIR}/rhasspy-snips-nlu-hermes/
$COPY rhasspy-speakers-cli-hermes/requirements.txt ${BUILD_DIR}/rhasspy-speakers-cli-hermes/
$COPY rhasspy-supervisor/requirements.txt ${BUILD_DIR}/rhasspy-supervisor/
$COPY rhasspy-tts-cli-hermes/requirements.txt ${BUILD_DIR}/rhasspy-tts-cli-hermes/
$COPY rhasspy-tts-wavenet-hermes/requirements.txt ${BUILD_DIR}/rhasspy-tts-wavenet-hermes/
$COPY rhasspy-wake-pocketsphinx-hermes/requirements.txt ${BUILD_DIR}/rhasspy-wake-pocketsphinx-hermes/
$COPY rhasspy-wake-raven/ ${BUILD_DIR}/rhasspy-wake-raven/
$COPY rhasspy-wake-raven-hermes/requirements.txt ${BUILD_DIR}/rhasspy-wake-raven-hermes/
$COPY rhasspy-tts-larynx-hermes/requirements.txt ${BUILD_DIR}/rhasspy-tts-larynx-hermes/


# Autoconf
$COPY m4/ ${BUILD_DIR}/m4/
$COPY configure config.sub config.guess \
     install-sh missing aclocal.m4 \
     Makefile.in setup.py.in setup.cfg rhasspy.sh.in rhasspy.spec.in \
     ${BUILD_DIR}/


 cd ${BUILD_DIR} && \
    ./configure $CONFIGURE_OPTS --enable-in-place --prefix=${APP_DIR}/.venv

cd ${BASE_DIR}

$COPY scripts/install/ ${BUILD_DIR}/scripts/install/

$COPY RHASSPY_DIRS ${BUILD_DIR}/

export PIP_INSTALL_ARGS="${PIP_INSTALL_ARGS} -f ${DOWNLOAD_DIR}/shared -f ${DOWNLOAD_DIR}/${TARGETARCH}${TARGETVARIANT}" && \
export PIP_VERSION='pip<=20.2.4' && \
if [ "${TARGETARCH}${TARGETVARIANT}" = 'amd64' ]; then \
    export PIP_PREINSTALL_PACKAGES="${PIP_PREINSTALL_PACKAGES} detect-simd~=0.2.0"; \
fi && \
export POCKETSPHINX_FROM_SRC=no && \
cd ${BUILD_DIR} && \
make $BUILD_OPTS && \
make install $BUILD_OPTS

mkdir -p ${APP_DIR}/rhasspy-wake-raven/rhasspywake_raven && \
    cp -f ${BUILD_DIR}/rhasspy-wake-raven/rhasspywake_raven/dtw*.so \
        ${APP_DIR}/rhasspy-wake-raven/rhasspywake_raven/

cd ${APP_DIR}/.venv && \
    find . -type f -name 'g2p.fst.gz' -exec gunzip -f {} \;


cd ${BASE_DIR}
$COPY etc/shflags ${APP_DIR}/etc/
$COPY etc/wav/ ${APP_DIR}/etc/wav/
$COPY bin/ ${APP_DIR}/bin/
$COPY VERSION RHASSPY_DIRS ${APP_DIR}/

# Copy Rhasspy source
$COPY rhasspy/ ${APP_DIR}/rhasspy/
$COPY rhasspy-server-hermes/ ${APP_DIR}/rhasspy-server-hermes/
$COPY rhasspy-wake-snowboy-hermes/ ${APP_DIR}/rhasspy-wake-snowboy-hermes/
$COPY rhasspy-wake-porcupine-hermes/ ${APP_DIR}/rhasspy-wake-porcupine-hermes/
$COPY rhasspy-wake-precise-hermes/ ${APP_DIR}/rhasspy-wake-precise-hermes/
$COPY rhasspy-profile/ ${APP_DIR}/rhasspy-profile/
$COPY rhasspy-asr/ ${APP_DIR}/rhasspy-asr/
$COPY rhasspy-asr-deepspeech/ ${APP_DIR}/rhasspy-asr-deepspeech/
$COPY rhasspy-asr-deepspeech-hermes/ ${APP_DIR}/rhasspy-asr-deepspeech-hermes/
$COPY rhasspy-asr-pocketsphinx/ ${APP_DIR}/rhasspy-asr-pocketsphinx/
$COPY rhasspy-asr-pocketsphinx-hermes/ ${APP_DIR}/rhasspy-asr-pocketsphinx-hermes/
$COPY rhasspy-asr-kaldi/ ${APP_DIR}/rhasspy-asr-kaldi/
$COPY rhasspy-asr-kaldi-hermes/ ${APP_DIR}/rhasspy-asr-kaldi-hermes/
$COPY rhasspy-asr-vosk-hermes/ ${APP_DIR}/rhasspy-asr-vosk-hermes/
$COPY rhasspy-dialogue-hermes/ ${APP_DIR}/rhasspy-dialogue-hermes/
$COPY rhasspy-fuzzywuzzy/ ${APP_DIR}/rhasspy-fuzzywuzzy/
$COPY rhasspy-fuzzywuzzy-hermes/ ${APP_DIR}/rhasspy-fuzzywuzzy-hermes/
$COPY rhasspy-hermes/ ${APP_DIR}/rhasspy-hermes/
$COPY rhasspy-homeassistant-hermes/ ${APP_DIR}/rhasspy-homeassistant-hermes/
$COPY rhasspy-microphone-cli-hermes/ ${APP_DIR}/rhasspy-microphone-cli-hermes/
$COPY rhasspy-microphone-pyaudio-hermes/ ${APP_DIR}/rhasspy-microphone-pyaudio-hermes/
$COPY rhasspy-nlu/ ${APP_DIR}/rhasspy-nlu/
$COPY rhasspy-nlu-hermes/ ${APP_DIR}/rhasspy-nlu-hermes/
$COPY rhasspy-rasa-nlu-hermes/ ${APP_DIR}/rhasspy-rasa-nlu-hermes/
$COPY rhasspy-remote-http-hermes/ ${APP_DIR}/rhasspy-remote-http-hermes/
$COPY rhasspy-silence/ ${APP_DIR}/rhasspy-silence/
$COPY rhasspy-snips-nlu/ ${APP_DIR}/rhasspy-snips-nlu/
$COPY rhasspy-snips-nlu-hermes/ ${APP_DIR}/rhasspy-snips-nlu-hermes/
$COPY rhasspy-speakers-cli-hermes/ ${APP_DIR}/rhasspy-speakers-cli-hermes/
$COPY rhasspy-supervisor/ ${APP_DIR}/rhasspy-supervisor/
$COPY rhasspy-tts-cli-hermes/ ${APP_DIR}/rhasspy-tts-cli-hermes/
$COPY rhasspy-tts-wavenet-hermes/ ${APP_DIR}/rhasspy-tts-wavenet-hermes/
$COPY rhasspy-wake-pocketsphinx-hermes/ ${APP_DIR}/rhasspy-wake-pocketsphinx-hermes/
$COPY rhasspy-wake-raven/ ${APP_DIR}/rhasspy-wake-raven/
$COPY rhasspy-wake-raven-hermes/ ${APP_DIR}/rhasspy-wake-raven-hermes/
$COPY rhasspy-tts-larynx-hermes/ ${APP_DIR}/rhasspy-tts-larynx-hermes/
