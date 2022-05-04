# DB-Neo4JAssignment

## Run
```
$ docker compose up
```

### Import Data
Creates each node and relationship between them
```cypher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/metrica-sports/sample-data/master/data/Sample_Game_1/Sample_Game_1_RawEventsData.csv' AS row
MERGE (tea:Team {name: row.Team})

MERGE (g:Game {name: 'Game 1'})
MERGE (tea)-[:PLAYS_IN]->(g)

MERGE (typ:Event {name: row.Type, startTime: row.`Start Time [s]`, endTime: row.`End Time [s]`})
MERGE (typ)-[:IN {period: row.Period}]->(g)

MERGE (pFrom:Player {name: row.From})
MERGE (pFrom)-[:PLAYS_ON]->(tea)
MERGE (pFrom)-[:CAUSED]->(typ)

FOREACH (ignore in CASE WHEN exists(row.To) THEN [1] ELSE [] END | 
    MERGE (pTo:Player {name: row.To})
    MERGE (pTo)-[:PLAYS_ON]->(tea)
    MERGE (typ)-[:RECIVES]->(pTo)
)

WITH row 
WHERE NOT row.Subtype IS NULL
MATCH (evn:Event {startTime: row.`Start Time [s]`, endTime: row.`End Time [s]`})
UNWIND split(row.Subtype, '-') AS subtype
MERGE (se:SubEvent {name: subtype})
MERGE (evn)-[:IS_ALSO]->(se)
```

_NOTE: Because of the way the csv data is structed, the current graph model shows both WON and LOSS  as Subtype nodes of a single CHALLENGE node._

# Graph Model
![Picture of graph model](asserts/graph_model.png)

# Usage

## Most passes and recives

```cypher
MATCH (p:Player)-[:CAUSED]->(e:Event)-[:RECIVES]->(p2:Player)
RETURN p.name AS name, count((p)-[:RECIVES]->(e)) as pass_count
ORDER BY pass_count DESC
```

```cypher
MATCH (p:Player)-[:CAUSED]->(e:Event)-[:RECIVES]->(p2:Player)
RETURN p2.name AS name, count((e)-[:RECIVES]->(p2)) as recive_count
ORDER BY recive_count DESC
```

![Most passes](asserts/5_most_passes.png) ![Most recives](asserts/5_most_recives.png)

If we look at the four players with most recives we get the graph below. 
The top cluster is the _home_ team, and the bottom is the _away_ team.

We can see the passes from each player is prette even, with the exception of one player on the away team that never pass or recived the ball to either of the two players.

![Most recive](asserts/two_most_recives_each_team.png)

The four players with most passes gives us a little diffrent picture. As before, the top team is the _home_ team and the bottom is the _away_ team.

![Most passes](asserts/most_passses.png)

In termes of passes, the home team seemes to be the best in that regard, and we go down the list to find the player on the _away_ team with second most passes its Player16 at place number 8 in the list.

The home team just seem to have more passes between each other compared to the away team.

## Goals and attempts

Here is all goals and attempted goals. There are a total of 11 attempts, 4 of which resulted in a goal.  

![Goal attemps](asserts/goals_and_attempts.png)

By including the players and their team we get a better understanding of how the match went.

![Goal attempts with players](asserts/goals_and_attempts_including_players.png)

The attempts were performed by a total of 7 players, three of which plays on the _away_ team and other four on the _home_ team.

All goals went to the _home_ team and it looks like it was a rough match for the _away_ team since they only made three attempts in total.
We can also see that Player9 attemped to score three times and two of his attempted resulted in goals. 

## Which team had the ball longest?

The following cypher command is used to retrieve the start and end time for all events separated into which team they belong to:

```cypher
MATCH (t:Team {name: 'Home'})<-[]-(:Player)-[:CAUSED]->(e:Event)
RETURN t.name AS Team, e.startTime AS startTime, e.endTime 
AS endTime
UNION
MATCH (t:Team {name: 'Away'})<-[]-(:Player)-[:CAUSED]->(e:Event)
RETURN t.name AS Team, e.startTime AS startTime, e.endTime 
AS endTime
```

We used python to calculate which team had possession of the ball the most. (See [./script.py](./script.py) for full implementation)

`event diff time` is the sum of all events from start to end time value. <br/>
`held time` is the sum of time between each event, its assummed that the team for the last event is the one in possession of the ball.

Output:
```
Home event diff time: 0:14:34.560000
Home held time: 0:35:14.640000
Home total possession time: 0:49:49.200000

Away event diff time: 0:12:48.760000
Away held time: 0:33:07.200000
Home total possession time: 0:45:55.960000

Total seconds: 5745.16
Match time: 1:35:45.160000
```

## Is there any closed ‘societies’ between players? (passing the ball to each other)
We use this cypher query to retrieve a list with number of passes between two players.

```cypher
MATCH (p:Player)-[:CAUSED]->(e:Event)-[:RECIVES]->(p2:Player), 
    (p2:Player)-[:CAUSED]->(e2:Event)-[:RECIVES]->(p:Player)
WITH p, p2, collect(e)+collect(e2) AS list
UNWIND list AS events
WITH DISTINCT p, p2, events
RETURN p.name AS player_1, p2.name AS player_2, count(events) AS pass_count
ORDER BY pass_count DESC
```

Output:

![Passes between players](asserts/most_passess_between_player_pair.png)

The query doesn’t return any data that can be used to show a graph, but we can change the return line to return p, p2, and events instead and thereby get the graph. Although, that wouldn’t make sense as we can get the same result by just using the following query:

```cypher
MATCH (p:Player)-[:CAUSED]->(e:Event)-[:RECIVES]->(p2:Player), 
    (p2:Player)-[:CAUSED]->(e2:Event)-[:RECIVES]->(p:Player)
RETURN *
```

If we just look at the whole graph over all passes between all players, it can be hard to extract any useful information besides some players making more passes than other:

![All passess between all players](asserts/passess_between_all_players.png)

If we go a little further and look at _Player2_ which have the most plays with _Player7_. We can see that _Player2_ mostly plays with _Player7_ and _Player3_.

![Player2 societies](asserts/all_player2_societies.png)

### Only shows players that have played the ball back and fought
The queries above are only meant to show players that have played the ball back and fought between each other. If we wanted to see all passes, we would use the query below:

```cypher
MATCH (p:Player)--(e:Event)--(p2:Player)
RETURN p, p2, e
```

This graph will also show players that have only received the ball from another player.

## How close is the connection between two specific players?

