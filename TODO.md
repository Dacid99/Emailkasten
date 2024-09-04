implement basic exchange
emaildbfeeder and mailparser should be factories or something more maintainable than right now
attachmentdatasize kinda small
different choices for fetching depending on protocol
custom fetching filters
storageModel
distinguish configs by env, db and user-immutables, migrate db settings to initial settings
autostart daemons on restart
custom additional healthchecks
restructure logging
return serialized db data after scan and fetch_all

# to test
request restriction and permissions
stats only for user
daemons still working?
list response of correspondents, interference with filtering?
autoincrementation if row already exists?
test stripped whitespace from body and subject

# to fix
weird behhaviour in daemon init daemonmodel is assigned to logger??

# at next db reset
use manytomanyfield thorugh the bridge table
start to use configurationmodel
static variables for field names

# remember
new migration must include setting of defaults
logpath is misconfigured to work on windows
csrf is disabled for debug
