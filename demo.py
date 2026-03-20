# demo.py — the master script
import os
from middleware import run_middleware
from knowledge_base_builder import build_knowledge_base, retrieve_context
from llm_engine import ask_llm
from voice_input import listen
from voice_output import speak
from config import SIMULATED_CSV, ENVIRONMENT

def initialise():
    print("Initialising Creta Assistant...")

    # Build knowledge base from current data
    csv_path = SIMULATED_CSV if ENVIRONMENT == "simulated" else get_live_csv()
    events   = run_middleware(csv_path)

    if events:
        build_knowledge_base(events)
        print(f"Knowledge base ready. {len(events)} events indexed.")
    else:
        print("No anomalies detected. Knowledge base empty — all systems normal.")

    print("\nCreta Assistant ready. Press ENTER to ask a question.\n")

def main():
    initialise()

    while True:
        input("Press ENTER to speak...")
        question = listen()

        if not question.strip():
            speak("I did not catch that. Please try again.")
            continue

        print(f"You asked: {question}")
        context = retrieve_context(question)
        answer  = ask_llm(question, context)
        print(f"Assistant: {answer}\n")
        speak(answer)

if __name__ == "__main__":
    main()