from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import SystemMessage, BaseOutputParser
from langchain.chains import LLMChain
from langchain.llms import OpenAI
import json
import re
import os


load_dotenv()
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.environ["MONGODB_ATLAS_CLUSTER_URI"])
db_name = "pymongo"
collection_name = "logging"
index_name = "return_status"
collection = client[db_name][collection_name]

llm = OpenAI()


class MonitoringParser(BaseOutputParser):
    def parse(self, text: str):
        json_object = {"message": "", "data": []}
        pattern = r"\[.*?\]"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            array_of_objects = match.group(0)
            json_object["data"] = array_of_objects

        json_object["message"] = re.sub(pattern, "", text)

        return json_object


@app.post("/monitoring-assistant")
async def assistant(request: Request):
    raw_body = await request.json()

    raw_result = collection.find({}, {"embedding": 0})
    result = list(raw_result)
    system_message = SystemMessage(content=str(result))
    question_template = HumanMessagePromptTemplate.from_template(
        "{text}, counting 4xx, and 5xx in request_status are considered as failed, error field is reason why it fail. Answer must contain , as seperator. Please summarize health of system everytime at the end."
    )
    monitoring_prompt = ChatPromptTemplate.from_messages(
        [system_message, question_template]
    )
    monitor_assistant = LLMChain(
        llm=llm, prompt=monitoring_prompt, output_parser=MonitoringParser()
    )

    return monitor_assistant.run(raw_body["text"])
