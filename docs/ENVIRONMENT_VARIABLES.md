export REDIS_URL=redis://192.168.0.225:6379/0
export CELERY_BROKER_URL=redis://192.168.0.225:6379/0

# OpenRouter (LLM)
export OPENROUTER_API_KEY=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
export LLM_MODEL=cognitivecomputations/dolphin-mistral-24b-venice-edition:free

# AWS S3 (Storage)
export S3_BUCKET_NAME=pdf2audiobook-r2
export AWS_ACCESS_KEY_ID=beb66e81ec66ea228152bb84d1715554
export AWS_ENDPOINT_URL=https://a814c2378497e13f32c27a6608cf2a4c.r2.cloudflarestorage.com
export AWS_SECRET_ACCESS_KEY=83feda17f7a0c1f6d2bbcb17f2a39ae033e21baf17c0737d86c67899e0b13d51

# OpenAI-Compatible TTS (Local Kokoro)
export OPENAI_BASE_URL=http://localhost:8880/v1
export OPENAI_TTS_MODEL=kokoro
export OPENAI_API_KEY=not-needed

# Kokoro Voice Mapping (Optional - defaults shown)
export KOKORO_VOICE_DEFAULT=af_sky+af_bella
export KOKORO_VOICE_FEMALE=af_bella
export KOKORO_VOICE_MALE=af_sky
# export KOKORO_VOICE_ALLOY=af_sky+af_bella
# export KOKORO_VOICE_ECHO=af_bella
# export KOKORO_VOICE_FABLE=af_sky
# export KOKORO_VOICE_ONYX=af_sky
# export KOKORO_VOICE_NOVA=af_bella
# export KOKORO_VOICE_SHIMMER=af_sky+af_bella

# Google Cloud TTS Configuration
# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
# export GOOGLE_API_KEY=

# Google TTS Costs (per 1M characters)
export GOOGLE_TTS_COST_STANDARD=4.0
export GOOGLE_TTS_COST_PREMIUM=30.0

# Google Voice Mappings
export GOOGLE_VOICE_US_FEMALE_STD=en-US-Wavenet-C
export GOOGLE_VOICE_US_MALE_STD=en-US-Wavenet-I
export GOOGLE_VOICE_GB_FEMALE_STD=en-GB-Wavenet-F
export GOOGLE_VOICE_GB_MALE_STD=en-GB-Wavenet-O
export GOOGLE_VOICE_US_FEMALE_PREMIUM=en-US-Studio-O
export GOOGLE_VOICE_US_MALE_PREMIUM=en-US-Studio-Q
export GOOGLE_VOICE_GB_FEMALE_PREMIUM=en-GB-Studio-C
export GOOGLE_VOICE_GB_MALE_PREMIUM=en-GB-Studio-B

# Application Settings
export ENVIRONMENT=development
export LOG_LEVEL=INFO
