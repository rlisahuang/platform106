from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "ACd15518a67e97932dc474c159e7c71a56"
# Your Auth Token from twilio.com/console
auth_token  = "e900a8ac4aba8611a8099c4f2311a22f"

client = Client(account_sid, auth_token)

try:
    message = client.messages.create(
    to="+13392243886", 
    from_="+18572675446",
    body="Hello from Python!")

    print(message.sid)
except Exception as err:
    print("text sent failed.")