local lc = require("luachild")

local p, r, w

r, w = lc.pipe()
p = lc.spawn{ 'sudo', '-ESk', 'docker', 'stop', 'project_planner_apsi_2024l_db_1', stdin = r}
r:close()
w:write(arg[1])
w:close()
p:wait()

r, w = lc.pipe()
p = lc.spawn{ 'sudo', '-ESk', 'docker', 'rm', 'project_planner_apsi_2024l_db_1', stdin = r}
r:close()
w:write(arg[1])
w:close()
p:wait()

r, w = lc.pipe()
p = lc.spawn{ 'sudo', '-ESk', 'docker-compose', 'up', '-d', stdin = r}
r:close()
w:write(arg[1])
w:close()
p:wait()

