import google
import os

print("google.__path__ =", google.__path__)
for path in google.__path__:
    print(f"Contents of {path}:")
    print(os.listdir(path))

from google import generativeai as genai
print(genai)

