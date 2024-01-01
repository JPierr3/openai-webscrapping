
import requests
import re 
from pydantic import BaseModel, Field
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser

openai_token = 'sk-JKyllUVz'
targetUrl = 'https://www.buscalibre.pe'
response = requests.get(targetUrl)
html_text = response.text

# Removeemos cosas innecesarias
html_text = re.sub(r'<head.*?>.*?</head>', '', html_text, flags=re.DOTALL)
html_text = re.sub(r'<script.*?>.*?</script>', '', html_text, flags=re.DOTALL)
html_text = re.sub(r'<style.*?>.*?</style>', '', html_text, flags=re.DOTALL)

# limitamos los caracteres para no sobrepasarnos
# con los limites de tokens de openai
html_text = html_text[:80000]



class Libro(BaseModel):
    """Información acerca de un libro"""
    titulo:      str = Field(..., description="Titulo del libro")
    puntuacion:  str = Field(..., description="Puntuación del libro")
    precio:      str = Field(..., description="Precio del libro")

from typing import List
class LibroScrapper(BaseModel):
    """Información para extraer de HTML raw data"""
    libros: List[Libro] = Field(..., description="Lista de información de Libros")



functions = [convert_pydantic_to_openai_function(LibroScrapper)]

model = ChatOpenAI(temperature=0, 
                   model_name='gpt-4-1106-preview', 
                   openai_api_key=openai_token).bind(functions=functions,   
                                                    function_call={"name": "LibroScrapper"})


prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en hacer web scraping y analizar HTML crudo"
                +", si no se proporciona explícitamente no supongas"),
    ("human", "{input}")
])

chain =  prompt | model | JsonKeyOutputFunctionsParser(key_name="libros")

result = chain.invoke({"input": html_text})

for libro in result:
    print(f"Título:     {libro['titulo']}")
    print(f"Puntuación: {libro['puntuacion']}")
    print(f"Precio:     {libro['precio']}")
    print("--------------------------------------------------")