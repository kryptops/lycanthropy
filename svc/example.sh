if netstat -antup | grep 68; then
  echo -e "\e[31m    WARNING!!!\e[0m"
  echo -e "\e[31m    THERE IS A SERVICE RUNNING ON :53. PLEASE HALT THIS SERVICE BEFORE STARTING THE LYCANTHROPY SERVER.\e[0m"
  read -p "    EXIT AND RECONFIGURE DNS[y/n]? " continuedata
  if [["$continuedata" == "y"]]; then
    echo "lmao" 
  fi
fi
