# Bedrock HTTPS API Setup

This repository contains instructions and scripts to set up and run multiple HTTPS-enabled Bedrock-based FastAPI services for **summarization** and **address detection** using AWS Bedrock models.

---

## 🐍 Python Installation (via Source)

If using an internal Nexus mirror, replace the Python download link accordingly.

```
# Download Python 3.12.x source
wget https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tgz

# Extract and enter the directory
tar -xf Python-3.12.5.tgz
cd Python-3.12.5
```

### Build and Install
```
./configure --enable-optimizations --with-ensurepip=install
make -j$(nproc)              # Use all available CPU cores
sudo make altinstall         # Avoid overwriting system python
```

### Set Python Path
```
export PATH="/usr/local/bin:$PATH"
sudo rm /usr/bin/python3
sudo ln -s /usr/local/bin/python3.12 /usr/bin/python3
python3.12 -m ensurepip --upgrade
sudo ln -s /usr/local/bin/pip3.12 /usr/local/bin/pip3
```

⚠️ **Note:** Ensure SSL is installed.  
If SSL modules are missing, revert to Python 3.9, install SSL, rebuild, and re-test.

```
sudo rm /usr/bin/python3
sudo ln -s /usr/bin/python3.9 /usr/bin/python3

# Rebuild with SSL support
./configure --enable-optimizations --with-ensurepip=install
make -j$(nproc)
sudo make altinstall

# Test SSL
python3.12 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

---

## 🐳 Docker Installation

```
# Update packages
sudo dnf update -y

# Install Docker
sudo dnf install -y docker

# Start and enable service
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 📦 Install Python Dependencies

```
pip3 install fastapi==0.115.14
pip3 install uvicorn[standard]==0.34.3
pip3 install pydantic==2.11.7
pip3 install openai==1.92.1
pip3 install python-dotenv==1.1.1
pip3 install httpx==0.28.1
pip3 install requests
pip3 install boto3
```

### OpenAI Key
Add your OpenAI key in your environment or `.env` file:
```
OPENAI_API_KEY=mi/p6JnS67Pgv5WEbs5E8pOEm389
```

---

## 🤖 Create Bedrock Application Inference Profiles (AIPs)

Run the following Python commands to create your AIPs.  
Update **model ARN** and **account ID** if needed.

```
python3 create_aip.py \
  --model-arn arn:aws:bedrock:us-east-1:196856463470:inference-profile/us.anthropic.claude-opus-4-20250514-v1:0 \
  --name my-claude-opus4-aip \
  --description "My Claude Opus 4 AIP for summarization and address detection"

python3 create_aip.py \
  --model-arn arn:aws:bedrock:us-east-1:196856463470:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0 \
  --name my-claude-sonnet4-aip \
  --description "My Claude Sonnet 4 AIP for summarization and address detection"
```

---

## 🔐 HTTPS Certificate Setup

Obtain or generate SSL certificate and key files and place them in the project root:

```
server.cert
server.key
```

---

## 🚀 Run HTTPS Bedrock Services

Start the FastAPI HTTPS servers using the AIPs created above.

```
python3 https_bedrock_multiple.py \
  --model-id arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/7njv6am2e610 \
  --port 7861 \
  --certfile server.cert \
  --keyfile server.key

python3 https_bedrock_multiple.py \
  --model-id arn:aws:bedrock:us-east-1:196856463470:application-inference-profile/sjmlz5l91sce \
  --port 7860 \
  --certfile server.cert \
  --keyfile server.key
```

---

## 🧩 Set Up as Systemd Services

Create and manage services to keep the APIs running continuously.

```
sudo vi /etc/systemd/system/bedrock7860.service
sudo vi /etc/systemd/system/bedrock7861.service
sudo vi /etc/systemd/system/bedrock-watchdog.timer
sudo vi /etc/systemd/system/bedrock-watchdog.service

sudo systemctl daemon-reload
sudo systemctl restart bedrock7860.service
sudo systemctl restart bedrock7861.service
sudo systemctl restart bedrock-watchdog.service
sudo systemctl status bedrock-watchdog.service
```

---

## 📜 Check Server Logs

```
# Home directory logs
tail -f /home/ssm-user/bedrock/bedrock7860.log
tail -f /home/ssm-user/bedrock/bedrock7861.log

# Or system logs
tail -f /var/log/bedrock7860.log
tail -f /var/log/bedrock7861.log
```

---

## 🧪 Sample cURL Tests

**Address Detection API**
```
curl -k -X POST "https://localhost:7861/address-detection" \
 -H "Content-Type: application/json" \
 -d '{
    "entity_urn": "urn:entity:1234",
    "content": "Our new office is located at 1600 Amphitheatre Parkway, Mountain View, CA 94043. Please visit us."
 }'
```

**Summarization API**
```
curl -k -X POST "http://localhost:7860/summarize" \
 -H "Content-Type: application/json" \
 -d '{
    "entity_urn": "urn:entity:5678",
    "content": "The customer was very happy with our service and said it was the best experience they have ever had."
 }'
```

---

## 🧾 Summary

| Component | Description |
|------------|--------------|
| **Python 3.12.5** | Custom compiled Python with SSL support |
| **FastAPI + Uvicorn** | Framework for serving Bedrock inference APIs |
| **Docker** | Optional containerization |
| **Systemd Services** | For continuous operation |
| **HTTPS Support** | Secured via SSL certificate |
| **AWS Bedrock Models** | Claude Opus 4 & Sonnet 4 used for summarization and address detection |

---

### ✅ Final Checklist
- [ ] Python 3.12 installed with SSL  
- [ ] Required Python packages installed  
- [ ] AIPs created in AWS Bedrock  
- [ ] SSL cert/key in place  
- [ ] HTTPS services started  
- [ ] Verified API responses via cURL  

---

**Author:** Karthik
**Version:** 1.0  
