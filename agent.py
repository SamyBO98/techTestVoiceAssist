#Manage asynchrone
import asyncio
#Manage to create agent, connect audio and manage conversation
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, tts as agents_tts, stt as agents_stt
#Manage to detect silence vs parole
from livekit.plugins import silero
#Manage AI for answers
from livekit.plugins import openai as livekit_openai
#Google Text to Speech mp3 to text
from gtts import gTTS
from dotenv import load_dotenv
import io
import numpy as np

import logging
logging.basicConfig(level=logging.WARNING)



#Load .env where there is all variables linked to the room i created in LiveKit
load_dotenv()
#load_dotenv(dotenv_path=r"C:\Users\samyb\OneDrive\Bureau\techTestVoiceAssist\.env")

#Base class for the vocal recognition
#Param = Agent Speak To Text
class FasterWhisperSTT(agents_stt.STT):
    #Base constructor
    def __init__(self, model: str = "small", language: str = "fr"):
        #Base constructor for STT
        #Capacity of our STT = real-time transcription + need the whole sentence (streaming False and interim_results=False )
        super().__init__(capabilities=agents_stt.STTCapabilities(
            streaming=False,
            interim_results=False,
        ))
        self._model_name = model
        self._language = language
        #Model small is big so no need to load it now -> use _load_model 
        self._model = None

    def _load_model(self):
        if self._model is None:
            #Import here because WhisperModel takes so much time    
            from faster_whisper import WhisperModel
            #self._model = WhisperModel(self._model_name, device="cpu", compute_type="int8") 
            self._model = WhisperModel(self._model_name, device="cuda", compute_type="float16")
        return self._model

    #Async like that agent can listen, talk and write at the same time
    #buffer = audio send by LiveKit
    #**kwargs = can add other params if needed
    #return LiveKit SpeechEvent (transcript text)
    async def _recognize_impl(self, buffer, **kwargs) -> agents_stt.SpeechEvent:
        #Transcription doesnt block agent
        loop = asyncio.get_event_loop()
        #convert audio to array of number + cast as float + normalise values
        pcm = np.frombuffer(buffer.data, dtype=np.int16).astype(np.float32) / 32768.0

        # Resampling 24000 → 16000 Hz
        import scipy.signal
        pcm = scipy.signal.resample(pcm, int(len(pcm) * 16000 / buffer.sample_rate))
 
        #Whisper blocks everytime (takes a lot of time + use GPU) so we exec it in another thread
        def _transcribe():
            model = self._load_model()
            #Allow us to recognize txt segments
            segments, _ = model.transcribe(pcm, language=self._language, beam_size=5, temperature=0.0)
            #Concatenate to have the full sentence
            return " ".join(s.text for s in segments).strip()

        #Run the function
        text = await loop.run_in_executor(None, _transcribe)
        print("Transcription : " + str(text))

        #Return final_transcript
        return agents_stt.SpeechEvent(
            type=agents_stt.SpeechEventType.FINAL_TRANSCRIPT,
            alternatives=[agents_stt.SpeechData(language=self._language, text=text)]
        )

#Voice of the agent Google Text-to-Speech
class GTTSPlugin(agents_tts.TTS):
    def __init__(self):
        super().__init__(
            capabilities=agents_tts.TTSCapabilities(streaming=False),
            sample_rate=24000,
            num_channels=1,
        )

    #Param text = text that i want to transform to speech
    #Return ChunkedStream (send audio by chunks) to read audio
    #Generate audio gTTS and convert to PCM
    def synthesize(self, text: str, **kwargs) -> agents_tts.ChunkedStream:
        return GTTSStream(self, text, conn_options=kwargs.get("conn_options"))


class GTTSStream(agents_tts.ChunkedStream):
    def __init__(self, tts, text: str, conn_options=None):
        super().__init__(tts=tts, input_text=text, conn_options=conn_options)
        self._text = text

    #Product the audio
    async def _run(self, output_emitter):
        #Exec heavy function in another thread (not blocking agent)
        loop = asyncio.get_event_loop()

        #Blocking function but after run_in_executor
        def _synth():
            #Transform txt to french voice
            tts_obj = gTTS(text=self._text, lang="fr")
            buf = io.BytesIO()
            #Write MP3 file to this buffer
            tts_obj.write_to_fp(buf)
            #Back to the beginning of the buffer to read it
            buf.seek(0)
            return buf.read()

        audio_bytes = await loop.run_in_executor(None, _synth)

        #MP3 to PCM
        def _convert():
            import pydub
            buf = io.BytesIO(audio_bytes)
            #Read audio
            audio = pydub.AudioSegment.from_mp3(buf)
            #24000 = better audio + mono + 2 octets (16 bits -> LiveKit is waiting for int16 PCM)
            #All TTS plugins must output audio as PCM int16 or float32. Mono is recommended for speech. (doc)
            #gTTS will be readable by LiveKit
            audio = audio.set_frame_rate(24000).set_channels(1).set_sample_width(2)
            return audio.raw_data
        
        #Run
        pcm_data = await loop.run_in_executor(None, _convert)

        #Init livekit flow
        output_emitter.initialize(
        request_id=self._text[:20],
        sample_rate=24000,
        num_channels=1,
        mime_type="audio/pcm",
        stream=True,        
        )
        #Send audio by segments
        output_emitter.start_segment(segment_id="0")
        output_emitter.push(pcm_data)
        output_emitter.end_segment()
        output_emitter.end_input()


#Testing Agent 
class TestAgent(Agent):
    #Static role here since LLM=None
    def __init__(self, ctx):
        super().__init__(instructions="""
        Tu es un assistant vocal francophone spécialisé dans la prise de rendez-vous.
        Réponds TOUJOURS en français, de manière courte et claire.
        Demande la date et l'heure souhaitées pour le rendez-vous.
        Quand l'utilisateur donne une date, confirme juste en disant "Parfait, votre rendez-vous est bien noté pour le [date]. Au revoir !".
        Ne dis JAMAIS que tu enregistres ou sauvegardes quoi que ce soit dans un système.
        Ne propose JAMAIS de modification de date.
        Reste naturel comme un vrai secrétaire au téléphone.
                         """)
        self._ctx = ctx

    #Say the sentence without blocking + can be interrupted if user talk while he is talking
    async def on_enter(self):
        await self.session.say("Bonjour. Quelle date vous conviendrait pour le rendez-vous ?", allow_interruptions=True)

    #Delay to hang up (End sentence + 5s)
    async def on_user_turn_completed(self, turn_ctx, new_message):
        await super().on_user_turn_completed(turn_ctx, new_message)
        asyncio.create_task(self._delayed_hangup(12))

    #Disconnect after delay
    async def _delayed_hangup(self, delay):
        await asyncio.sleep(delay)
        print("=== HANG UP ===")
        try:
            await self._ctx.room.disconnect()
        except Exception:
            pass



async def entrypoint(ctx: agents.JobContext):
    #Connect to the room with .env data
    await ctx.connect()

    agent = TestAgent(ctx)

    #VAD = Voice Activity Detection
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=FasterWhisperSTT(model="small", language="fr"),
        llm=livekit_openai.LLM(
        model="gemma2:2b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        ),
        tts=GTTSPlugin(),
    )

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(),
    )


# ───── CLI ─────
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))