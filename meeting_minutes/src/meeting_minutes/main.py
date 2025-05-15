#!/usr/bin/env python
from openai import OpenAI
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from pydub import AudioSegment
from pydub.utils import make_chunks
from pathlib import Path
from crews.meeting_minutes_crew.meeting_minutes_crew import MeetingMinutesCrew
from crews.gmailcrew.gmailcrew import GmailCrew
import agentops
import os

from dotenv import load_dotenv
load_dotenv()

client = OpenAI()


class MeetingMinutesState(BaseModel):
    transcript: str = ""
    meeting_minutes: str = ""


class MeetingMinutesFlow(Flow[MeetingMinutesState]):

    @start()
    def transcribe_meeting(self):
        print("generating Transcribe")


        SCRIPT_DIR = Path(__file__).parent
        audio_path = str(SCRIPT_DIR/"EarningsCall.wav")

        #load the audio file
        audio = AudioSegment.from_file(audio_path, format = "wav")

        chunk_length_ms = 60000
        chunks = make_chunks(audio , chunk_length_ms)

        full_transcription = ""
        for i,chunk in enumerate(chunks):
            print(f"Transcribing chunk {i+1}/{len(chunks)}")
            chunk_path = f"chunk_{i}.wav"
            chunk.export(chunk_path, format= "wav")

            with open(chunk_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                full_transcription += transcription.text + " "

        self.state.transcript = full_transcription
        print(f"Transcription: {self.state.transcript}")

    @listen(transcribe_meeting)
    def generate_meeting_minutes(self):
        print("Generating Meeting Minutes")

        crew = MeetingMinutesCrew()

        inputs = {
            "transcript": self.state.transcript
        }
        meeting_minutes = crew.crew().kickoff(inputs)
        self.state.meeting_minutes = meeting_minutes


    @listen(generate_meeting_minutes)
    def create_draft_meeting_minutes(self):
        print("Creating Draft Meeting Minutes")

        crew = GmailCrew()

        inputs = {
            "body": str(self.state.meeting_minutes)
            # "body": """- Tyler to oversee the completion of the customer feedback analysis report. (Due next meeting)
            #             - Development team (led by Michael) to focus on the integration of the AI module. (Ongoing)
            #             - Jessica to prepare and circulate a detailed plan for the new marketing campaigns. (By next week)
            #             - Organize a cross-department workshop. Emily to draft a proposal. (Proposal due by the end of the month)
            #         """
        }

        draft_crew = crew.crew().kickoff(inputs)
        print(f"Draft_crew {draft_crew}")


def kickoff():
    session = agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))
    meeting_minutes_flow = MeetingMinutesFlow()
    meeting_minutes_flow.plot()
    meeting_minutes_flow.kickoff()

    session.end_session()




if __name__ == "__main__":
    kickoff()
