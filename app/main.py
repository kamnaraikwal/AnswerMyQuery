import speech_recognition as sr

from langgraph.checkpoint.mongodb import MongoDBSaver
from .graph import create_chat_graph
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
 
# each thread is unique to a user, creates isolation of data
config = {"configurable": {"thread_id": "1"}}

def main():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer=checkpointer)
                        
        r = sr.Recognizer()

        #activating microphone
        with sr.Microphone() as source:
            # listen for 1 second to calibrate the energy threshold for ambient noise levels (noise cancellation)
            # time consuming
            r.adjust_for_ambient_noise(source)  

            # waits for x sec to listen to user if user doesn't speak
            ## r.pause_threshold = 2

            # loop so that it can be paused by user control (ctrl+C)
            while True:
                print("Say something!")
                audio = r.listen(source)
                # process audio
                sst=  r.recognize_google(audio)
                print("You said : ", sst)

                # 'values' streams the full value of the state after each step of the graph.
                # -1 for most recent message only
                for event in graph.stream({ "messages": [{"role": "user", "content": sst}] }, config, stream_mode="values"):
                    if "messages" in event:
                        event["messages"][-1].pretty_print()


main()