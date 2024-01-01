from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from pydantic import BaseModel, Field
from typing import List
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser

openai_token = 'sk-JKyllU'

targetUrl = 'https://www.google.com/maps/search/cevicheria/@-8.1057547,-79.048051,14z/data=!3m1!4b1?entry=ttu' 
op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome(options=op)
driver.get(targetUrl)
driver.implicitly_wait(1) 

# conseguimos el html crudo
html_text = driver.page_source
html_text_truncado = html_text[800000:]
#print((html_text_truncado))
driver.quit()



class Local(BaseModel):
    """Información acerca de un Local, restaurante"""
    posicion: int = Field(..., description="Posición ")
    nombre: str = Field(..., description="Nombre exacto del restaurante")
    calificacion: str = Field(..., description="Calificación promedio otorgada por los usuarios")
    total_opiniones: str = Field(..., description="Número total de opiniones de los usuarios")
    precio: str = Field(..., description="Rango de precios")
    tipo: str = Field(..., description="Tipo de restaurante ")
    direccion: str = Field(..., description="Dirección física del restaurante")
    telefono: str = Field(..., description="Número de teléfono del restaurante")
    horario: str = Field(..., description="Horario de funcionamiento del restaurante")
    opciones_servicio: str = Field(..., description="Opciones de servicio disponibles")

class LocalesScrapper(BaseModel):
    """Analice muy bien los detalles de los resultados locales a partir de los datos HTML sin procesar de Google MAPS"""
    locales: List[Local] = Field(..., description="Lista de información de restaurantes")

functions = [convert_pydantic_to_openai_function(LocalesScrapper)]

model = ChatOpenAI(temperature=0, 
                   model_name='gpt-4-1106-preview', 
                   openai_api_key=openai_token).bind(functions=functions,  
                                                     function_call={"name": "LocalesScrapper"})

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en el web scraping de restaurante de Google Maps. Extrae todos  los datos de los resultados de restaurantes locales. Si no se proporciona información explícitamente, no supongas"),
    ("human", "{input}")
])

chain =  prompt | model | JsonKeyOutputFunctionsParser(key_name="locales")

result = chain.invoke({"input": html_text_truncado})

for local in result:
    print(f"Nombre: {local['nombre']}")
    print(f"Calificación: {local['calificacion']}")
    print(f"Total Opiniones: {local['total_opiniones']}")
    print(f"Precio: {local['precio']}")
    print(f"Tipo: {local['tipo']}")
    print(f"Dirección: {local['direccion']}")
    print(f"Teléfono: {local['telefono']}")
    print(f"Horario: {local['horario']}")
    print(f"Opciones de Servicio: {local['opciones_servicio']}")
    print("--------------------------------------------------")