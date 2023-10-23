import os
import vertexai
from vertexai.language_models import TextGenerationModel
from collections import OrderedDict

class LLMHandler:
    
    def __init__(self, project_id: str, location: str, credentials_path: str, model_name: str = "text-bison"):
        self.parameters = {
            "max_output_tokens": 2000,
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40
        }
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        vertexai.init(project=project_id, location=location)
        self.model = TextGenerationModel.from_pretrained(model_name)

    def predict(self, text):
        response = self.model.predict(
                f"""{text}
                """, **self.parameters
        )
        return response.text

