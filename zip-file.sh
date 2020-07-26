
deactivate
ROOT_PWD=`pwd`
rm -rf ./function.zip

cd ./venv/lib/python3.8/site-packages
zip -r9 ${ROOT_PWD}/function.zip .

cd ${ROOT_PWD}
zip -g function.zip handler.py