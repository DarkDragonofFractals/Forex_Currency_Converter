from ai import call_gpt

print("Attempting a simple AI call...")
try:
    response = call_gpt("What is the capital of France?")
    print("Success! Response:")
    print(response)
except Exception as e:
    print("The simple test failed with an error:")
    print(e)