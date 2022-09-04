import sqlite3
import requests


connection = sqlite3.connect("auction.db")
c = connection.cursor()

url = "https://bringatrailer.com/wp-json/bringatrailer/1.0/data/keyword-filter"
querystring = {"page": "1", "range": "30D", "sort": "td", "results": "items"}

# IMPORTANT: May need to replace header and the one below using Insomnia tool
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://bringatrailer.com/auctions/results/?timeFrame=month",
    "x-wp-nonce": "c0e68e4cdf",
    "Connection": "keep-alive",
    "Cookie": "bat_tracking_data_alt={'conversion':0,'datetime':1651864916,'redirect':'https://bringatrailer.com/listing/2018-porsche-911-gt2-rs-weissach-24/','referrer':""}; __stripe_mid=ffff27de-fb6b-4cb6-b8d9-133879a57b63be68ca; OptanonConsent=isIABGlobal=false&datestamp=Sat+Sep+03+2022+11%3A39%3A53+GMT-0700+(Pacific+Daylight+Saving+Time)&version=6.39.0&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CSPD_BG%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false; usprivacy=1---; _ga=GA1.2.1142735446.1651864919; __gads=ID=665a7ae599549f3f:T=1651864919:S=ALNI_MYOyp9zFV_390cwk7ovZ18BXAJZqA; __gpi=UID=000004f7a898fd34:T=1651864919:RT=1662230391:S=ALNI_MbZmc6YVpcrgAGCR0-_PSvNkesTig; OneTrustWPCCPAGoogleOptOut=false; subscribe_checkbox_7f934e8f367cd1991ef8af2c0ccfabdb=unchecked; iterableEndUserId=lancecj%40gmail.com; s_sess=%20s_cc%3Dtrue%3B; PHPSESSID=fbe524d61269e008307101958bb06bdf; __stripe_sid=bd786b66-634d-47fd-977e-71c21f19a4f99aeb65; _gid=GA1.2.800330770.1662230391; _gat=1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}
data = requests.request("GET", url, headers=headers, params=querystring)

json_resp = data.json()
total = json_resp['total']
pages = int(total/32 + 1)

for x in range(1,pages):
    querystring = {"page":f"{x}","range":"30D","sort":"td","results":"items"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://bringatrailer.com/auctions/results/?timeFrame=month",
        "x-wp-nonce": "c0e68e4cdf",
        "Connection": "keep-alive",
        "Cookie": "bat_tracking_data_alt={'conversion':0,'datetime':1651864916,'redirect':'https://bringatrailer.com/listing/2018-porsche-911-gt2-rs-weissach-24/','referrer':""}; __stripe_mid=ffff27de-fb6b-4cb6-b8d9-133879a57b63be68ca; OptanonConsent=isIABGlobal=false&datestamp=Sat+Sep+03+2022+11%3A39%3A53+GMT-0700+(Pacific+Daylight+Saving+Time)&version=6.39.0&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CSPD_BG%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false; usprivacy=1---; _ga=GA1.2.1142735446.1651864919; __gads=ID=665a7ae599549f3f:T=1651864919:S=ALNI_MYOyp9zFV_390cwk7ovZ18BXAJZqA; __gpi=UID=000004f7a898fd34:T=1651864919:RT=1662230391:S=ALNI_MbZmc6YVpcrgAGCR0-_PSvNkesTig; OneTrustWPCCPAGoogleOptOut=false; subscribe_checkbox_7f934e8f367cd1991ef8af2c0ccfabdb=unchecked; iterableEndUserId=lancecj%40gmail.com; s_sess=%20s_cc%3Dtrue%3B; PHPSESSID=fbe524d61269e008307101958bb06bdf; __stripe_sid=bd786b66-634d-47fd-977e-71c21f19a4f99aeb65; _gid=GA1.2.800330770.1662230391; _gat=1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }
    data = requests.request("GET", url, headers=headers, params=querystring)
    json_resp = data.json()

    for item in json_resp['items']:
        listing_url = item['url']
        try:
            if c.execute('''INSERT OR IGNORE INTO bat_pages (url,scraped) VALUES(?,0)''', (listing_url,)):
                print("Record inserted successfully!")
                connection.commit()
        except sqlite3.OperationalError as error:
            print("Failed to update table", error)
            pass

    connection.commit()
c.close()