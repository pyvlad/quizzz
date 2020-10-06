#!/bin/bash

cd ansible && ansible-playbook -i hosts/staging.yml main.yml;
cd ..
