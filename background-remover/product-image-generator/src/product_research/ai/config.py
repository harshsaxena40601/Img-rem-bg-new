AI_PROVIDERS = [

    {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "enabled": True,
        "max_attempts": 3,

        "capabilities": [
            "text",
            "vision",
        ],
    },
# 	{
#     "provider": "gemini",
#     "model": "fake-model-for-testing",
#     "enabled": True,
#     "max_attempts": 2,
#     "capabilities": [
#         "text",
#         "vision",
#     ],
# },

    {
        "provider": "groq",
        "model": "qwen/qwen3.6-27b",
        "enabled": True,
        "max_attempts": 2,

        "capabilities": [
            "text",
            "vision",
        ],
    },

]