import time

print("Hello World from Family Expenses Tracker!")

# Keep the container running for a bit so we can see the logs if needed, 
# or just exit if that's preferred for a simple test. 
# For an addon, it's usually a service, so let's loop.
while True:
    time.sleep(60)
    print("Heartbeat...")
