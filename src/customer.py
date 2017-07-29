import requests, json
from logger import logger
from geopy.geocoders import Nominatim

class Lookup:
    def __init__(self, settings):
        self.cust_id_url = settings["cust_id_url"]
        self.profiles_url = settings["profiles_url"]
        self.locn_url = settings["locn_url"]
        self.header = settings["http_header"]

    def lookup(self, msg):
        fname1 = ""
        location = {}
        cust_id = ""
        address = {}
        location["address"] = address
        emails_info = ""

        try:
            # Get customer id from mobile no
            mob = self.get_sender_no(msg)
            logger.info(mob)
            # Check customer id info from mob_no.
            cust_info = requests.get(self.cust_id_url + mob, headers=self.header)
            if cust_info.status_code == 200:
                cust_info_json = json.loads(cust_info.text)
                logger.info(cust_info_json)
                cust_info_options = cust_info_json["options"]
                logger.info(cust_info_options)
                option = cust_info_options[0]
                if option:
                    cust_id = option["payload"]["id"]
                    logger.info(cust_id)
                    if cust_id:
                        # Update the mobile number now
                        self.update_num(mob, cust_id)

                        # Now proceed to fetch the name
                        customer_resp = requests.get(self.profiles_url + "/" + str(cust_id) + "/", headers=self.header)
                        if customer_resp.status_code == 200:
                            customer = json.loads(customer_resp.text)
                            logger.info(customer["name"])
                            name = customer["name"]
                            if name:
                                fname = name.split()
                                if fname:
                                    fname1 = fname[0]
                                    logger.info("Name: " + fname1)

                            # Fetch the email now
                            emails = customer["emails"]
                            count = len(emails)
                            if emails:
                                for email in emails:
                                    count -= 1
                                    emails_info += email["email"]
                                    if count != 0:
                                        emails_info += ", "

                    # Fetch the location info now
                    cu_accnt_resp = requests.get(self.locn_url + "/" + mob + "/", headers=self.header)
                    if cu_accnt_resp.status_code == 200:
                        cu_accnt = json.loads(cu_accnt_resp.text)
                        logger.info(cu_accnt_resp.text)
                        devices = cu_accnt["devices"]
                        for device in devices:
                            geo_location = device["location"]
                            location["geo"] = geo_location

                            # Now update the locality details
                            coord = geo_location["geometry"]["coordinates"]
                            coord_rev_str = str(coord[1]) + "," + str(coord[0])
                            logger.info(coord_rev_str)
                            geolocator = Nominatim()
                            loc = geolocator.reverse(coord_rev_str)
                            location["locality"], location["zipcode"] = self.build_locality(loc.raw)
                            address["street"] = loc.address
                            location["tag"] = "Last Known"
                            location = json.dumps(location)

                            # Update in the profiles DB now
                            self.update_locn(location, cust_id)
        except:
            location = json.dumps(location)
            import logging
            logging.exception("JARVIS2: Could not connect to GeoLocation APIs")

        return fname1, location, emails_info, cust_id

    def update_num(self, mob_num, cust_id):
        num_url = self.profiles_url + str(cust_id) + "/numbers/"
        resp = requests.get(num_url, headers=self.header)
        updated = False
        if resp.status_code == 200:
            resp_txt_json = json.loads(resp.text)
            resp_result = resp_txt_json["results"]
            for result in resp_result:
                if result["number"] == mob_num:
                    updated = True
                    break
            if not updated:
                num_data = {"numbers" : str(mob_num), "tag" : "Last Known"}
                requests.post(num_url, data=num_data, headers=self.header)

    def update_locn(self, location, cust_id):
        # Post locations to locations DB
        prof_location_url = self.profiles_url + "/" + str(cust_id) + "/locations/"
        resp = requests.get(prof_location_url, headers=self.header)
        loc_id = -1
        if resp.status_code == 200:
            resp_txt_json = json.loads(resp.text)
            resp_result = resp_txt_json["results"]
            for result in resp_result:
                if result["tag"] == "Last Known":
                    loc_id = result["id"]
                    break
        if loc_id != -1:
            prof_location_url += str(loc_id) + "/"
            #logger.info("Location URL1: " + prof_location_url)
            requests.patch(prof_location_url, data=location, headers=self.header)
        else:
            #logger.info("Location URL2: " + prof_location_url)
            requests.post(prof_location_url, data=location, headers=self.header)

    def build_locality(self, loc_raw):
        locality = ""
        zipcode = ""
        if loc_raw:
            address = loc_raw["address"]
            logger.info(address)
            if address:
                if address.get("country"):
                    locality += address["country"] + "/"

                if address.get("state"):
                    locality += address["state"] + "/"

                if address.get("city"):
                    locality += address["city"] + "/"

                if address.get("suburb"):
                    locality += address["suburb"]

                zipcode = address.get("postcode")
        return locality, zipcode

    def get_sender_no(self, msg):
        sender = str(msg["from"])
        return sender.split("@")[0]