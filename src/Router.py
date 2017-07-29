import requests, json
from logger import logger

class Router:

    def __init__(self, settings):
        self.agents_url = settings["agents_url"]
        self.skills_url = settings["skills_url"]
        self.header = settings["http_header"]

    def route(self, order_dict, chat_id, chat_bot_id):
        team = "pilot" #Defaults to pilot
        intents = order_dict["intents"]
        logger.info("Chat id: " + str(chat_id))
        logger.info("Order info: " + str(order_dict))

        if intents:
            team = "general"
        agent_to_route = self.get_active_agents(team, chat_bot_id, self.header)
        logger.info("Agent to route: " + json.dumps(agent_to_route))
        if agent_to_route != "":
            self.route_to_agent(agent_to_route, chat_id, intents, chat_bot_id, self.header)
        else:
            raise RuntimeError("Unable to route to agent. None available!")

    def route_to_agent(self, agent, chat_id, intents, chat_bot_id, header):
        target_agent = agent["id"]
        notes = ''
        status = 20
        cat = "Unknown"
        if intents:
            status = 30
            count = 1
            for intent in intents:
                cat = intent["category"]["type"]
                sub_cat = intent["subCategory"]["type"]
                req = intent["subCategory"]["intent"]
                notes += str(count) + ". Customer " + req + " to get " + sub_cat + "\n"
                count += 1
        title = "Order Summary: " + cat
        body = json.dumps({u"category" : cat, u"title" : title, u"agent" : target_agent, u"notes" : notes,
                           u"status": status})
        url = self.agents_url + str(chat_bot_id) + "/chats/" + str(chat_id) + "/"
        resp = requests.patch(url, data=body, headers=header)
        if resp.status_code != 200:
            raise RuntimeError("Unable to route to agent! " + resp.text)

    def get_active_agents(self, input_team, chat_bot_id, header):
        logger.info("Input team = " + input_team)
        candidate_agents = []
        resp = requests.get(self.agents_url, headers=header)
        if resp.status_code == 200:
            logger.info("Got list of agents...")
            result = json.loads(resp.text)
            if result:
                agents = result["results"]
                active_agents = self.filter_active_agents(agents)
                logger.info("Got list of active agents...")
                # From active agents, retrieve details & load info
                for agent in active_agents:
                    agent_id = agent["id"]
                    if agent_id == chat_bot_id:
                        pass
                    agent_team_resp = requests.get(self.skills_url + str(agent_id) + "/teams/", headers=header)
                    if agent_team_resp.status_code == 200:
                        agent_team_result = json.loads(agent_team_resp.text)
                        teams = agent_team_result["results"]
                        logger.info("Got agent team/skills...")
                        logger.info(teams)
                        for team in teams:
                            if team["team"] == input_team:
                                logger.info("Appending agent to candidate list...")
                                candidate_agents.append(agent)
                    else:
                        raise RuntimeError("Unable to get list of active agents! " + agent_team_resp.text)
            else:
                raise RuntimeError("Unable to get list of agents!")
        else:
            raise RuntimeError("Unable to get list of agents! " + resp.text)

        sorted_cand_agents = sorted(candidate_agents, key=lambda k: k.get('num_assigned_chats', 0), reverse=False)
        logger.info(sorted_cand_agents)
        if sorted_cand_agents:
            return sorted_cand_agents[0]
        else:
            return ""

    def filter_active_agents(self, agents):
        active_agents = []
        for agent in agents:
            if agent["status"] == 30 or agent["status"] == 20:
                # This person is now active. Take her.
                active_agents.append(agent)
        return active_agents