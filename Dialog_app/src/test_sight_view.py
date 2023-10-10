from utils.config_reader import read_config


from database.mongodb_tools_Dialog import MongoDB,check_db_exists,SightseeingDBHandler,SightViewTCPServer



Sightseeing_mongodb = SightseeingDBHandler("Sightseeing_Spot_DB")
sightID_ls = [80026003,80026022,80025993,80025990]

view_spot_json = Sightseeing_mongodb.create_send_json(sightID_ls)

config = read_config()

IP = config.get("Server_Info","Server_ip")
sight_view = SightViewTCPServer(IP,config.get("Server_Info","SiteViewer_port"))


sight_view.send_data(view_spot_json)