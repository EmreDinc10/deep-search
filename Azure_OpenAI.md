### Running Inference and getting the Model Output with Azure AI

```python
from dotenv import load_dotenv
import os
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()

openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_key = os.getenv("AZURE_OPENAI_KEY")

client_o3 = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=openai_endpoint,  # predefined
    api_key=openai_key              # predefined
)

resp = client_o3.chat.completions.create(
    model="o3-mini",
    messages=[
        {"role": "system", "content": 
        """
					<System prompt>
				"""},
        {"role": "user", "content": "<question, query>"},
    ]
)

print(resp.choices[0].message.content)

```