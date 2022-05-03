from datetime import datetime, timedelta
from neo4j import GraphDatabase, Session
import neo4j

query = '''MATCH (t:Team {name: 'Home'})<-[]-(:Player)-[:CAUSED]->(e:Event)
RETURN t.name AS Team, e.startTime AS startTime, e.endTime 
AS endTime
UNION
MATCH (t:Team {name: 'Away'})<-[]-(:Player)-[:CAUSED]->(e:Event)
RETURN t.name AS Team, e.startTime AS startTime, e.endTime 
AS endTime'''

class Event:
    def __init__(self, dict: dict):
        self.team = dict['Team']
        self.startTime = float(dict['startTime'])
        self.endTime = float(dict['endTime'])


if __name__ == "__main__":
    db: neo4j.Driver = GraphDatabase.driver("neo4j://localhost:7687/", auth=("neo4j", "1234"))
    with db:
        session: Session = db.session()
        with session: 
            result = session.run(query)

            list = [ Event(item) for item in result.data() ]
            list.sort(key=lambda x: x.startTime)

            homeEventDiffTime = 0
            homeHeldTime = 0
            awayEventDiffTime = 0
            awayHeldTime = 0

            for index, item in enumerate(list):
                if item.team == "Home":
                    homeEventDiffTime += item.endTime - item.startTime
                elif item.team == "Away":
                    awayEventDiffTime += item.endTime - item.startTime
                
                if index > 0:
                    prevItem = list[index - 1]
                    diffPrevEvent = item.startTime - prevItem.endTime
                    if prevItem.team == 'Home':
                        homeHeldTime += diffPrevEvent
                    elif prevItem.team == 'Away':
                        awayHeldTime += diffPrevEvent
                        


            print(f'Home event diff time: {timedelta(seconds=homeEventDiffTime)}')
            print(f'Home held time: {timedelta(seconds=homeHeldTime)}')
            print(f'Home total possession time: {timedelta(seconds=homeEventDiffTime + homeHeldTime)}')
            print(f'\nAway event diff time: {timedelta(seconds=awayEventDiffTime)}')
            print(f'Away held time: {timedelta(seconds=awayHeldTime)}')
            print(f'Home total possession time: {timedelta(seconds=awayEventDiffTime + awayHeldTime)}')

            totalMatchTime = homeEventDiffTime + homeHeldTime + awayEventDiffTime + awayHeldTime
            print(f'\nTotal seconds: {totalMatchTime}')
            print(f'Match time: {timedelta(seconds=totalMatchTime)}')