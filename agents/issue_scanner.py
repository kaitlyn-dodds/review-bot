# Is triggered w/ a repo (config data) passed in
# agent should verify repo exists
# check for repo state (create state file if no state exists)
# verify if agent should run 
    # is there an open issue-bot pr open?
    # has the project changed since last run (compare commit hash)
# if agent should run, pull latest project files
# feed prompt and data into claude
# create new branch w/ name of agent and commit hash 
# commit proposed changes to the KNOWN_ISSUES file  
# open pr under bot name
# ?? would be nice to include some sort of notification system, but out of scope for now



