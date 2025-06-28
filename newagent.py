from omnidimension import Client
import time

client = Client("YOUR_API_KEY")

response = client.agent.create(
    name="SupportAssistant",
    welcome_message="Hi! I’m here to help you with support queries.",
    context_breakdown=[
        {"title": "Intent", "body": "Classify user goals.", "is_enabled": True},
        {"title": "Topic", "body": "Understand product/service references.", "is_enabled": True}
    ],
    transcriber={
        "provider": "deepgram_stream",
        "model": "nova-3",
        "silence_timeout_ms": 400,
        "numerals": True,
        "punctuate": True
    },
    model={
        "model": "gpt-4o-mini",
        "temperature": 0.7
    },
    voice={
        "provider": "eleven_labs",
        "voice_id": "cgSgspJ2msm6clMCkdW9"
    }
)

agent_id = response.get("json", {}).get("id")
print(f"Created agent ID: {agent_id}")

for i in range(30):
    status_response = client.agent.get(agent_id)
    print(f"Raw status response: {status_response}")

    # Try to safely extract the status
    status = None
    if isinstance(status_response, dict):
        # Sometimes the response key might be 'json' or 'data', let's check both
        if "json" in status_response:
            status = status_response["json"].get("status")
        elif "data" in status_response:
            status = status_response["data"].get("status")
        else:
            # Maybe status_response itself is the agent dict
            status = status_response.get("status")

    print(f"Agent status: {status}")

    if status == "Completed":
        print("Agent is ready!")
        break

    time.sleep(2)
else:
    print("Agent creation timed out, please try again later.")

