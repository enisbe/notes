# llm_handler.py

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
        self.chat_model = TextGenerationModel.from_pretrained(model_name)
    
    def llm_summary(self, content: str) -> str:
        """
        Uses the LLM model to generate a summary of the given content.

        Args:
        - content (str): The content to be summarized.

        Returns:
        - str: The summarized content.
        """
        if content in ['\r\n', "\n"]:
            return content
        else:
            response = self.chat_model.predict(
                f"""text:\n{content}\n Summarize the previous text.
                """, **self.parameters
            )
            return response.text
    
    def process_content(self, doc: OrderedDict, func, key: str = '') -> OrderedDict:
        """
        Iterates over the document and applies a given function.

        Args:
        - doc (OrderedDict): The document to be processed.
        - func (function): The function to be applied to the content.
        - key (str): An optional key to target specific parts of the document.

        Returns:
        - OrderedDict: The processed document.
        """
        if key:
            new_doc = OrderedDict({key: OrderedDict()})
            new_doc[key] = self._process_content_inner(doc, func)
            return new_doc
        else:
            return self._process_content_inner(doc, func)

    def _process_content_inner(self, doc: OrderedDict, func) -> OrderedDict:
        """
        Inner recursive function to iterate over the document and apply a function.

        Args:
        - doc (OrderedDict): The document to be processed.
        - func (function): The function to be applied to the content.

        Returns:
        - OrderedDict: The processed document.
        """
        if isinstance(doc, dict):
            new_doc = OrderedDict()
            for k, value in doc.items():
                if k == 'content':
                    new_doc[k] = func(value)
                else:
                    new_doc[k] = self._process_content_inner(value, func)
            return new_doc
        else:
            return doc

