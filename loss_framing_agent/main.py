import pandas as pd
import matplotlib
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import openai

print("pandas:", pd.__version__)
print("matplotlib:", matplotlib.__version__)
print("VADER OK:", SentimentIntensityAnalyzer() is not None)
print("openai:", openai.__version__)
print("\nAll libraries working! Ready for Step 3.")