```bash
sudo lsof -t -i tcp:80 -s tcp:listen | sudo xargs kill;\
alias cls=clear;\
alias py=python3.10;\
source venv/bin/activate;\
uvicorn server.api:app --host 0.0.0.0 --port 80 --workers 4
```