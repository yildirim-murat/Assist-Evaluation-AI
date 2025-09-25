def get_audio_downloader(list_of_audios: dict):
    # ucid_list = list_of_audios.get("UCID list", [])
    
    # results = []
    # # sadece ilk 5 elemanı kontrol et
    # for ucid in ucid_list[:5]:
    #     if str(ucid).startswith("88"):

    #         #https://seskayit.ng112.gov.tr/SesKayit/webresources/ses/getKayitDetay?token=eebaf359-605c-4872-a5b3-b33679d091c5&ucid=10600064641758808711&classified=1&incidentId=0&isEngelsiz=false
    #         results.append({"UCID": ucid, "status": "OK"})
    #     else:
    #         results.append({"UCID": ucid, "status": "FAILED"})
    
    # return results
    print("Audio downloader completed" + str(list_of_audios))
    return {"status": "Audio downloader completed"}