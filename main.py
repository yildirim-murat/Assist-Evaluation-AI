import requests
import os
from datetime import datetime, timedelta

token = "d76fa9af-ded0-4310-a8c3-9efb61e72a11"
baslangicTar = "2025-09-19"

agent_id="30699032"


save_dir = "data"
os.makedirs(save_dir, exist_ok=True)

start_date = datetime.strptime(baslangicTar, "%Y-%m-%d")
end_date = start_date + timedelta(days=7)
bitisTar = end_date.strftime("%Y-%m-%d")

url1 = "https://seskayit.ng112.gov.tr/SesKayit/webresources/ses/getKayit"
params1 = {
    "token": token,
    "baslangicTar": baslangicTar,
    "baslangicSaat": "00:00",
    "bitisTar": bitisTar,
    "bitisSaat": "00:00",
    "callId": "",
    "arayanNumara": "",
    "arananNumara": "",
    "callType": 0,
    "agentid": agent_id,
    "vakaId": "",
    "crsAramasi": 0
}

resp1 = requests.get(url1, params=params1)
resp1.raise_for_status()

data1 = resp1.json().get("data", [])

dosyaad_list = []

url2 = "https://seskayit.ng112.gov.tr/SesKayit/webresources/ses/getKayitDetay"
for item in data1:
    ucid = item.get("UCID")
    incident_id = item.get("INCIDENTID")
    if not ucid:
        continue

    params2 = {
        "token": token,
        "ucid": ucid,
        "classified": 1,
        "incidentId": incident_id,
        "isEngelsiz": "false"
    }
    
    resp2 = requests.get(url2, params=params2)

    if resp2.status_code == 200:
        data2 = resp2.json().get("data", [])
        for detay in data2:
            agent_id = str(detay.get("AGENTS", ""))
            if agent_id.startswith("30699"):
                dosyaad = detay.get("DOSYAD")
                if dosyaad:
                    dosyaad_list.append(dosyaad)

print("Dosya Adları:" + ", ".join(dosyaad_list))

def get_ip_from_prefix(prefix: str) -> str:
    """
    21 -> 115
    22 -> 116
    23 -> 117
    24 -> 118
    """
    mapping = {
        "21": "115",
        "22": "116",
        "23": "117",
        "24": "118",
    }
    return mapping.get(prefix, "114")

for dosyaad in dosyaad_list:
    # Örn: 880622003156993 -> prefix '22'
    prefix = dosyaad[4:6]
    ip_part = get_ip_from_prefix(prefix)

    # XML dosyası için URL
    xml_url = f"http://10.106.102.{ip_part}/records/{dosyaad[6:9]}/{dosyaad[9:11]}/{dosyaad[11:13]}/{dosyaad}.xml"

    try:
        wav_url = xml_url.replace(".xml", ".wav")
        print(f"İndiriliyor: {wav_url}")

        wav_resp = requests.get(wav_url, stream=True)
        wav_resp.raise_for_status()

        filename = os.path.join(save_dir, dosyaad + ".wav")
        with open(filename, "wb") as f:
            for chunk in wav_resp.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Kaydedildi: {filename}")

    except Exception as e:
        print(f"Hata: {e}")