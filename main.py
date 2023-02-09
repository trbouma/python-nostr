from nostr.client.client import NostrClient
from nostr.event import Event
from nostr.key import PublicKey
import asyncio
import threading
import time
import datetime


def print_status(client):
    print("")
    for relay in client.relay_manager.relays.values():
        connected_text = "🟢" if relay.connected else "🔴"
        status_text = f"{connected_text} ⬆️ {relay.num_sent_events} ⬇️ {relay.num_received_events} ⚠️ {relay.error_counter} ⏱️ {relay.ping} ms - {relay.url.split('//')[1]}"
        print(status_text)


async def dm():
    print("This is an example NIP-04 DM flow")
    pk = input("Enter your privatekey to post from (enter nothing for a random one): ")

    def callback(event: Event, decrypted_content):
        """
        Callback to trigger when a DM is received.
        """
        print(
            f"\nFrom {event.public_key[:3]}..{event.public_key[-3:]}: {decrypted_content}"
        )

    client = NostrClient(privatekey_hex=pk)
    if not pk:
        print(f"Your private key: {client.private_key.hex()}")

    print(f"Your public key: {client.public_key.hex()}")

    # await asyncio.sleep(1)
    t = threading.Thread(
        target=client.get_dm,
        args=(
            client.public_key,
            callback,
        ),
    )
    t.start()

    to_pubk_hex = (
        input("Enter other pubkey to post to (enter nothing to DM yourself): ")
        or client.public_key.hex()
    )
    print(f"Subscribing to DMs to {to_pubk_hex}")
    while True:
        print_status(client)
        await asyncio.sleep(1)
        msg = input("\nEnter message: ")
        client.dm(msg, PublicKey(bytes.fromhex(to_pubk_hex)))


async def post():
    print("This posts and reads a nostr note")
    pk = input("Enter your privatekey to post from (enter nothing for a random one): ")

    def callback(event: Event):
        """
        Callback to trigger when post appers.
        """
        print(
            f"\nFrom {event.public_key[:3]}..{event.public_key[-3:]}: {event.content}"
        )

    sender_client = NostrClient(privatekey_hex=pk)
    # await asyncio.sleep(1)

    to_pubk_hex = (
        input(
            "Enter other pubkey (enter nothing to read your own posts, enter * for all): "
        )
        or sender_client.public_key.hex()
    )
    if to_pubk_hex == "*":
        to_pubk = None
    else:
        print(f"Subscribing to posts by {to_pubk_hex}")
        to_pubk = PublicKey(bytes.fromhex(to_pubk_hex))

    filters = {
        "since": int(
            time.mktime(
                (datetime.datetime.now() - datetime.timedelta(hours=1)).timetuple()
            )
        )
    }

    t = threading.Thread(
        target=sender_client.get_post,
        args=(
            to_pubk,
            callback,
            filters,
        ),
    )
    t.start()

    while True:
        print_status(sender_client)
        await asyncio.sleep(1)
        msg = input("\nEnter post: ")
        sender_client.post(msg)


if input("Enter '1' for DM, '2' for Posts (Default: 1):") or 1 == 1:
    # write a DM and receive DMs
    asyncio.run(dm())
else:
    # make a post and subscribe to posts
    asyncio.run(post())
