import time
from utils.config_reader import read_config


from database.mongodb_tools_Dialog import MongoDB,check_db_exists,SightseeingDBHandler,SightViewTCPServer



Sightseeing_mongodb = SightseeingDBHandler("Sightseeing_Spot_DB")
sightID_ls = [80026003,80026022,80025993,80025990]

view_spot_json = Sightseeing_mongodb.create_send_json(sightID_ls)

config = read_config()

IP = config.get("Server_Info","Server_ip")
sight_view = SightViewTCPServer(IP,config.get("Server_Info","SiteViewer_port"))
print(view_spot_json)

sight_view.send_data(view_spot_json)
time.sleep(3)
dictsite = {
    'Num': 3,
    'ImageURL1': 'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/SI_80025982_147763.jpg',
    'MapURL1': 'https://www.google.co.jp/maps/@35.059816866,135.758512863,15z',
    'Name1': '大田神社',
    'ImageURL2': 'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/SI_80026022_124509.jpg',
    'MapURL2': 'https://www.google.co.jp/maps/@35.060411266,135.75270778,15z',
    'Name2': '賀茂別雷神社(上賀茂神社)',
    'ImageURL3': 'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/SI_80026009_36306.jpg',
    'MapURL3': 'https://www.google.co.jp/maps/dir/34.8024907,135.7704978/%E4%BA%AC%E7%94%B0%E8%BE%BA%E9%A7%85/@34.8114904,135.7595635,15z/data=!3m1!4b1!4m8!4m7!1m0!1m5!1m1!1s0x6001176b77090dcb:0x896bea7c1d2d92be!2m2!1d135.768811!2d34.8208344?entry=ttu',
    'Name3': '源光庵'
}

sight_view.send_data(dictsite)

dictsite = {
    'Num': 3,
    'ImageURL1': 'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/SI_80025982_147763.jpg',
    'MapURL1': 'https://www.google.co.jp/maps/@35.059816866,135.758512863,15z',
    'Name1': '大田神社',
    'ImageURL2': 'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/SI_80026022_124509.jpg',
    'MapURL2': 'https://www.google.co.jp/maps/@35.060411266,135.75270778,15z',
    'Name2': '賀茂別雷神社(上賀茂神社)',
    'ImageURL3': 'https://www.j-jti.com/Storage/Image/Product/SightImage/Org/SI_80026009_36306.jpg',
    'MapURL3': 'https://www.google.co.jp/maps/dir/34.8024907,135.7704978/%E4%BA%AC%E7%94%B0%E8%BE%BA%E9%A7%85/@34.8114904,135.7595635,15z/data=!3m1!4b1!4m8!4m7!1m0!1m5!1m1!1s0x6001176b77090dcb:0x896bea7c1d2d92be!2m2!1d135.768811!2d34.8208344?entry=ttu',
    'Name3': '源光庵'
}
time.sleep(3)
dictsite = {
    'Num': 1,
    'ImageURL1': "https://www.j-jti.com/Storage/Image/Product/SightImage/Org/SI_80025982_147763.jpg",
    'MapURL1': 'https://www.google.co.jp/maps/@35.059816866,135.758512863,15z',
    'Name1': '大田神社',
}

sight_view.send_data(dictsite)