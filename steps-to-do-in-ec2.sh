wget https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tgz # Replace with the desired 3.12 version
tar -xf Python-3.12.6.tgz
cd Python-3.12.0



# Configure, build, and install
./configure --enable-optimizations --with-ensurepip=install
make -j$(nproc) # Use all available CPU cores for faster compilation
sudo make altinstall # Use altinstall to avoid overwriting default python


https://huggingface.co/spaces/snvskiit/content_processor/tree/main

export PATH="/usr/local/bin:$PATH"
sudo rm /usr/bin/python3
sudo ln -s /usr/local/bin/python3.12 /usr/bin/python3


python3.12 -m ensurepip --upgrade
sudo ln -s /usr/local/bin/pip3.12 /usr/local/bin/pip3

--make sure ssl is iinstalled. esle remove above link(3.12) and point it back to 3.9 and install dnf ssl and then rebuild below steps and test if ssl is available for latest pip


sudo rm /usr/bin/python3
sudo ln -s /usr/bin/python3.9 /usr/bin/python3


./configure --enable-optimizations --with-ensurepip=install
make -j$(nproc) # Use all available CPU cores for faster compilation
sudo make altinstall # Use altinstall to avoid overwriting default python
python3.12 -c "import ssl; print(ssl.OPENSSL_VERSION)"


Install DOcker: 
# Update packages
sudo dnf update -y


# Install Docker
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker


pip3 install fastapi==0.115.14
pip3 install uvicorn[standard]==0.34.3
pip3 install pydantic==2.11.7
pip3 install openai==1.92.1
pip3 install python-dotenv==1.1.1
pip3 install httpx==0.28.1
pip3 install requests
pip3 install boto3

openAI key: mi/p6JnS67Pgv5WEbs5E8pOEm389



########################CURL Commands Testing port 7860###############################


curl -X POST "http://localhost:7860/address-detection" \
     -H "Content-Type: application/json" \
     -H "x-api-key: mi/p6JnS67Pgv5WEbs5E8pOEm389" \
     -d '{
       "entity_urn": "test_001",
       "content": "Please send the package to 123 Main Street, New York, NY 10001"
     }'



curl -X POST "http://localhost:7860/summarize" \
     -H "Content-Type: application/json" \
     -H "x-api-key: mi/p6JnS67Pgv5WEbs5E8pOEm389" \
     -d '{
       "entity_urn": "test_002",
       "content": "I love this product! It exceeded my expectations..."
     }'



########################CURL Commands Testing port 7861###############################


curl -X POST "http://localhost:7861/address-detection" \
     -H "Content-Type: application/json" \
     -H "x-api-key: mi/p6JnS67Pgv5WEbs5E8pOEm389" \
     -d '{
       "entity_urn": "test_001",
       "content": "Please send the package to 123 Main Street, New York, NY 10001"
     }'



curl -X POST "http://localhost:7861/summarize" \
     -H "Content-Type: application/json" \
     -H "x-api-key: mi/p6JnS67Pgv5WEbs5E8pOEm389" \
     -d '{
       "entity_urn": "test_002",
       "content": "I love this product! It exceeded my expectations..."
     }'



AIPs in the Sandbox account" 


arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/iwsgqc9ip24v - drpem2-inference-profile
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/y4j0tcuyxnse - bala-modelid-inference-profile
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/qyzg4wencwp2 - bala-modelid-inference-profile
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/3zv2f0wamzd4 - sonnet-app-inference-profile
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/jdhrix5yj7vt - sonnet-app-inference-profile
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/qquft48uwxia - dzd_5idy2dkxrdmfl3 6dqu27rlwsqucn
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/nnk00bcfgg7i - dzd_5idy2dkxrdmfl3 6dqu27rlwsqucn
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/o3lusa9udpoh - anthcld37sonv1
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/gihg3g6p6t3k - anthcld37sonv1
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/35kedmlwvrqy - anthcld35sonv1
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/385toy4v8hy4 - anthcld37sonv1
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/8ao7jip49h5s - dzd_5idy2dkxrdmfl3 6dqu27rlwsqucn
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/3mfjs0vg28gm - dzd_5idy2dkxrdmfl3 6dqu27rlwsqucn
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/9436jzaia8su - dzd_5idy2dkxrdmfl3 6dqu27rlwsqucn
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/tig46ox2mi0k - dzd_5idy2dkxrdmfl3 aiahmddyh5kskn
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/w5h49m84b6nv - dzd_5idy2dkxrdmfl3 6dqu27rlwsqucn
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/7njv6am2e610 Claude Opus4
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/sjmlz5l91sce Claude Sonnet 4

################################# CURLS for Bedrock # ####################################################


curl -k -X POST "https://localhost:7861/address-detection" \
 -H "Content-Type: application/json" \
 -d '{
    "entity_urn": "urn:entity:1234",
    "content": "Our new office is located at 1600 Amphitheatre Parkway, Mountain View, CA 94043. Please visit us."
   }'



curl -k -X POST "http://localhost:7860/summarize" \
 -H "Content-Type: application/json" \
 -d '{
    "entity_urn": "urn:entity:5678",
    "content": "The customer was very happy with our service and said it was the best experience they have ever had."
   }'


--Python Commands to create new AIPs 


python3 create_aip.py \
 --model-arn arn:aws:bedrock:us-east-1:196856463470:inference-profile/us.anthropic.claude-opus-4-20250514-v1:0 \
 --name my-claude-opus4-aip \
 --description "My Claude Opus 4 AIP for summarization and address detection"



python3 create_aip.py \
 --model-arn arn:aws:bedrock:us-east-1:196856463470:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0 \
 --name my-claude-sonnet4-aip \
 --description "My Claude Sonnet 4 AIP for summarization and address detection"



##############################################


docker build -t bedrock-api .
docker run -d --name bedrock1 -p 7860:7860 -e MODEL_ID=arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/7njv6am2e610 -e PORT=7860 bedrock-api
docker run -d --name bedrock2 -p 7861:7861 -e MODEL_ID=arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/sjmlz5l91sce -e PORT=7861 bedrock-api
docker rm -f bedrock1 bedrock2 -- if names are already used
./start_bedrock_containers.sh


# Test container 1 on port 7860
curl http://127.0.0.1:7860/health


# Test container 2 on port 7861
curl https://127.0.0.1:443/health


python3 https_bedrock_multiple.py \
 --model-id arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/7njv6am2e610 \
 --port 7861\
 --certfile server.cert \
 --keyfile server.key

python3 https_bedrock_multiple.py \
 --model-id arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/sjmlz5l91sce \
 --port 7860\
 --certfile server.cert \
 --keyfile server.key


sudo vi /etc/systemd/system/bedrock7860.service
sudo vi /etc/systemd/system/bedrock7861.service


sudo systemctl daemon-reload
sudo systemctl restart bedrock7860.service
sudo systemctl restart bedrock7861.service


sudo systemctl daemon-reload
sudo systemctl restart bedrock-watchdog.service
sudo systemctl status bedrock-watchdog.service



check server logs: 
tail -f /var/log/bedrock7860.log
tail -f /var/log/bedrock7861.log


arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/zpxfizihhbgp --> Sonnet 4.5
arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/9ujinf0lfswg --> Llama Scout 4


python3 https_bedrock_multiple.py \
 --model-id arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/zpxfizihhbgp \
 --port 7862\
 --certfile server.cert \
 --keyfile server.key

python3 https_bedrock_multiple.py \
 --model-id arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/9ujinf0lfswg \
 --port 7863\
 --certfile server.cert \
 --keyfile server.key
