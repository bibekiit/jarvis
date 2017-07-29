import os, sys, logging, json, requests, signal

from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.stanzabase import ElementBase

from ChatBot2 import ChatBot2
from logger import logger

from Router import Router
from TextAnalytics import TextAnalytics

# Absolute path
abs_path = os.path.dirname(os.path.abspath('__file__'))

# Agent status on the realm
DISABLE_STATUS = 10
PAUSE_STATUS = 20
ACTIVE_STATUS = 30

class ReceivedXML(ElementBase):
	name = 'received'
	namespace = "urn:xmpp:chat-markers:0"

class DisplayedXML(ElementBase):
	name = 'displayed'
	namespace = "urn:xmpp:chat-markers:0"

# Jarvis2 virtual agent
class Jarvis2Bot(ClientXMPP):

    # Constructor
    def __init__(self, settings):
        self.settings = settings
        self.chat_bot_id = settings["bot_id"]
        self.virgin_order_dict = {'routing':False, 'intents' : [], 'Username':'', 'email':'', 'Cityname':''}

        # Load classifier
        logger.info("JARVIS2: Loading Text Analytics modules now...")
        self.cl = TextAnalytics().getCl()

        # TODO: Get username and passwd from API call instead of the settings file

        # Connect to Xmpp
        jid = settings["jid"]
        password = settings["password"]
        ClientXMPP.__init__(self, jid, password)

        # Register the handler routines
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        # Tell everyone in valhalla that I'm alive & kicking! BTW, Status=30 means active in our lingo.
        # Please excuse me for this convoluted and hard-coded method, Ok?
        self.update_bot_status(ACTIVE_STATUS)

        # Cache of Chatbots that Jarvis2 is managing
        self.bots = {}

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):

        logger.info("Jarvis2 is processing terminate request...")
        # Check if there are any active chats that should be requeued
        my_chats_resp = requests.get(self.settings["me_url"], headers=self.settings["http_header"])
        if my_chats_resp.status_code == 200:
            result = json.loads(my_chats_resp.text)
            num_chats = result["num_assigned_chats"]
            chats = []
            if num_chats != 0:
                chats_url = self.settings["agents_url"] + str(self.chat_bot_id) + "/chats/"
                chats_resp = requests.get(chats_url, headers=self.settings["http_header"])
                if chats_resp.status_code == 200:
                    chats_resp_json = json.loads(chats_resp.text)
                    chats = chats_resp_json["results"]
                    logger.info(chats)
                else:
                    logger.info(chats_resp.status_code)
        else:
            logger.info(my_chats_resp.text)
        logger.info("Jarvis2 is reassigning outstanding chats to active agents...")

        # Requeue to pilot team members before exiting
        router = Router(settings)
        for chat_id in chats:
            logger.info("Reassigning chat id: " + str(chat_id))
            router.route(self.virgin_order_dict, chat_id, self.chat_bot_id)

        logger.info("Jarvis2 is now terminating. Goodbye!!")
        # Now, safe to exit
        sys.exit(0)

    # Updates the status of Jarvis2 or other virtual agents
    def update_bot_status(self, status):
        logger.info("Setting agent status to: " + str(status))
        agents_url = self.settings["agents_url"] + "/" + str(settings["bot_id"]) + "/"
        stat_data = json.dumps({ "status" : status })
        resp = requests.patch(agents_url, data=stat_data, headers=settings["http_header"])

    # Tell Xmpp world that I'm present
    def session_start(self, event):
        self.send_presence()

    # Message event handler
    def message(self, msg):
        logger.info(msg)
        self.ack_received_message(msg)
        bye_msg = "Bye"

        chat_id = -1
        key = msg['from']
        if not self.bots.has_key(key):
            self.bots[key] = ChatBot2(settings, self)
        bot = self.bots[key]
        try:
            self.ack_displayed_message(msg)
            resp, order_dict, chat_id = bot.processMsg(msg, self.cl)
            # if not order_dict:
            #     order_dict = virgin_order_dict
            if resp == bye_msg:
                # Keep backend happy, refreshed and synced up
                requests.get(self.settings["me_url"], headers=self.settings["http_header"])
                Router(settings).route(order_dict, chat_id, self.chat_bot_id)
                self.bots.pop(key)
        except Exception:
            logging.exception("JARVIS2: Something awful happened!")
            bot.reset_order()
            if chat_id == -1:
                msg_str = str(msg)
                msg_tokens = msg_str.split()
                logger.info("Extracting chat id...")
                for token in msg_tokens:
                    if "chat_thread" in token:
                        chat_id = token.split("=")[1][1:-1]
            # Keep backend happy, refreshed and synced up
            requests.get(self.settings["me_url"], headers=self.settings["http_header"])
            Router(settings).route(self.virgin_order_dict, chat_id, self.chat_bot_id)
            self.bots.pop(key)


    def ack_received_message(self, msg):
        """
        <message to="recharge_bot@stage-c.magictiger.com/matrix" from="9591418090@stage-c.magictiger.com/mtx-android" id="" mt_routed="false" type="chat"><received xmlns="urn:xmpp:chat-markers:0" id="d6b58c0c-96d3-4361-9845-c8ada62acd41">d6b58c0c-96d3-4361-9845-c8ada62acd41</received><meta /></message>
        """
        try:
            msg_xml = self.make_message(mto=msg['from'], mfrom=msg['to'])
            msg_xml.xml.set('from', str(self.boundjid))
            msg_xml.xml.set('type',"chat")
            msg_xml.xml.set('mt_routed',"false")
            received_xml = ReceivedXML()
            received_xml['id'] = msg['id']
            received_xml.setup()
            received_xml.xml.text = msg['id']
            msg_xml.append(received_xml)
            logger.info('Received Tick')
            logger.info(msg_xml)
            resp = msg_xml.send()
        except Exception as e:
            logging.error(e)


    def ack_displayed_message(self, msg):
        """
        <message to="recharge_bot@stage-c.magictiger.com/matrix" from="9591418090@stage-c.magictiger.com/mtx-android" id="" mt_routed="false" type="chat"><displayed xmlns="urn:xmpp:chat-markers:0" id="d6b58c0c-96d3-4361-9845-c8ada62acd41">d6b58c0c-96d3-4361-9845-c8ada62acd41</displayed><meta /></message>
        """
        try:
            msg_xml = self.make_message(mto=msg['from'], mfrom=msg['to'])
            msg_xml.xml.set('from', str(self.boundjid))
            msg_xml.xml.set('type',"chat")
            msg_xml.xml.set('mt_routed',"false")
            displayed_xml = DisplayedXML()
            displayed_xml['id'] = msg['id']
            displayed_xml.setup()
            displayed_xml.xml.text = msg['id']
            msg_xml.append(displayed_xml)
            logger.info('Displayed Tick')
            logger.info(msg_xml)
            resp = msg_xml.send()
        except Exception as e:
            logging.error(e)

# Outside the Jarvis2 class, used to load the user supplied settings
def load_settings(deploy_env):
    ret = True
    settings = {}
    if len(deploy_env) != 2:
        usage()
        ret = False
    else:
        try:
            with open(abs_path + "/../config/settings.json") as json_file:
                json_data = json.load(json_file)
                if deploy_env[1] == "stage":
                    settings = json_data["stage"]
                elif deploy_env[1] == "local":
                    settings = json_data["local"]
                elif deploy_env[1] == "prod":
                    settings = json_data["prod"]
                else:
                    print "You have a corrupt 'data/settings.json' file. Giving up..contact developer now! :("
                    ret = False
        except:
            logging.exception("JARVIS2: Something awful happened!")
            ret = False
    return ret, settings

# Prints usage details
def usage():
    print "python XmppJarvis2.py <deployment_env>"
    print "Where deployment_env = local | stage | prod"

# Main!
if __name__ == '__main__':

    ret, settings = load_settings(sys.argv)
    if ret:
        # Set log levels
        logging.basicConfig(level=settings["log_level"],
                        format=settings["log_fmt"])

        # Instantiate the Jarvis2 bot
        xmpp = Jarvis2Bot(settings)

        # Connect now
        logger.info("JARVIS2: Connecting XMPP...")
        xmpp.connect()

        # Block wait for someone to ping now! Between you and me, it's really boring not to chat... :-|
        logger.info("JARVIS2: Ready to process messages...")
        xmpp.process(block=True)
    else:
        print "JARVIS2: FATAL ERROR! Terminating Jarvis2 due to errors..."