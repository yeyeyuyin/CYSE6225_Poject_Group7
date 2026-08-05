# EC2 Deployment Notes

1. **Launch instance**: Ubuntu 22.04/24.04 LTS, t3.micro is enough for a
   class project. Attach an IAM role granting DynamoDB access (see
   `dynamodb-policy.json` for a minimal example policy).
2. **Security group**: allow inbound 22 (SSH, ideally restricted to your IP),
   80 (HTTP), and 443 if you set up TLS.
3. **Clone the repo** to `/opt/webvideofinder`:
   ```bash
   sudo git clone <your-repo-url> /opt/webvideofinder
   ```
4. **Configure environment**: copy
   `/opt/webvideofinder/CYSE6225-Final-Project/backend/.env.example` to
   `/opt/webvideofinder/CYSE6225-Final-Project/backend/.env` and fill in
   `JWT_SECRET`, `AWS_REGION`, `TABLE_PREFIX`, etc. Since the instance has an
   IAM role, you do **not** need to put AWS access keys in `.env` — boto3
   picks up the role automatically.
5. **Create the DynamoDB tables** (from your local machine or the instance):
   ```bash
   python3 /opt/webvideofinder/CYSE6225-Final-Project/infra/dynamodb/create_tables.py --region us-east-1 --prefix dev_
   ```
6. **Run the bootstrap script**:
   ```bash
   cd /opt/webvideofinder/CYSE6225-Final-Project/infra/ec2
   sudo bash setup.sh
   ```
7. **Verify**:
   ```bash
   curl http://<ec2-public-ip>/api/health
   ```
   and open `http://<ec2-public-ip>/` in a browser for the frontend.

## Updating after a `git pull`

```bash
sudo systemctl restart webvideofinder
```

## TLS (stretch goal)

Point a domain at the instance's Elastic IP, then use Certbot:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```
