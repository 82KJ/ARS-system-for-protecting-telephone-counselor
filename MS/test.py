import vito

if __name__ == "__main__":

    CLIENT_ID = "OILciM2Ejz-eWlN2E-pE"
    CLIENT_SECRET = "qJIBUAPPhJApFpRXLGWJUiajeeaA1Y3hBdGx6pMc"

    client = vito.VITOOpenAPIClient(CLIENT_ID, CLIENT_SECRET)
    fname = "test_voice.wav"
    vito.asyncio.run(client.streaming_transcribe(fname))
