import os
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

# Generate a JWT token to authenticate a user in the LiveKit room
# identity = unique user ID, name = display name
token = (
    AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET'))
    .with_identity('user-test')
    .with_name('User Test')
    # Grant permission to join the specific room
    .with_grants(VideoGrants(room_join=True, room='test-room'))
    .to_jwt()
)
# Paste this token in the LiveKit playground to connect and interact with the agent
print(token)
print("url : wss://voiceassist-uco62cre.livekit.cloud" )
