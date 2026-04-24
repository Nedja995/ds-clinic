# Gemini Model pamareters

"""
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#generationconfig

Temperature controls response randomness.
Lower values (min 0) are deterministic and better for factual tasks,
while higher values increase creativity.
If responses are too generic or loop, adjust the temperature (at least 0.1).
"""

"""
https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/inference#generationconfig

If specified, nucleus sampling is used.
Top-P changes how the model selects tokens for output. Tokens are selected from the most (see top-K) to least probable until the sum of their probabilities equals the top-P value. For example, if tokens A, B, and C have a probability of 0.3, 0.2, and 0.1 and the top-P value is 0.5, then the model will select either A or B as the next token by using temperature and excludes C as a candidate.
Specify a lower value for less random responses and a higher value for more random responses.
"""
