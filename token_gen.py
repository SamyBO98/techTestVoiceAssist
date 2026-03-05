import os
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

token = (
    AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET'))
    .with_identity('user-test')
    .with_name('User Test')
    .with_grants(VideoGrants(room_join=True, room='test-room'))
    .to_jwt()
)
print(token)
print("url : wss://voiceassist-uco62cre.livekit.cloud" )