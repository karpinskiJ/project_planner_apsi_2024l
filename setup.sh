sudo -ESk docker stop project_planner_apsi_2024l_db_1 <<< $1
sudo -ESk docker rm project_planner_apsi_2024l_db_1 <<< $1
sudo -ESk docker-compose up -d <<< $1
