pipenv run pycodestyle webotron/*py
echo -e "\n\n\n\n\n"
pipenv run pydocstyle webotron/*py
echo -e "\n\n\n\n\n"
pipenv run pylint webotron/*py
echo -e "\n\n\n\n\n"
