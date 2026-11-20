#!/usr/bin/env python3
"""用 Gmail SMTP 发外联邮件。

凭据：.secrets/gmail.txt，两行即可
    address=you@gmail.com
    app_password=xxxxxxxxxxxxxxxx      # Google 应用专用密码，16 位，去掉空格

用法：
    python3 scripts/send-mail.py --draft reports/2026-11-18-vgsources-email-send.txt --dry-run
    python3 scripts/send-mail.py --draft reports/2026-11-18-vgsources-email-send.txt
"""
import argparse
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS = ROOT / ".secrets" / "gmail.txt"


def load_creds(path: Path):
    if not path.exists():
        sys.exit(f"缺少凭据文件：{path}\n按 .secrets/README.txt 里 Gmail 那节填两行。")
    conf = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            conf[k.strip().lower()] = v.strip()
    addr = conf.get("address") or conf.get("email") or conf.get("user")
    pwd = (conf.get("app_password") or conf.get("password") or conf.get("pass") or "").replace(" ", "")
    if not addr or not pwd:
        sys.exit("凭据文件里缺少 address= 或 app_password= 行。")
    host = conf.get("smtp_host", "smtp.gmail.com")
    port = int(conf.get("smtp_port", "465"))
    return addr, pwd, host, port


def parse_draft(path: Path):
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    to = subj = None
    body_start = 0
    for i, line in enumerate(lines):
        low = line.lower()
        if low.startswith("to:"):
            to = line.split(":", 1)[1].strip()
        elif low.startswith("subject:"):
            subj = line.split(":", 1)[1].strip()
        elif line.strip() == "" and (to or subj):
            body_start = i + 1
            break
    if not to or not subj:
        sys.exit("草稿缺少 To: 或 Subject: 头。")
    body = "\n".join(lines[body_start:]).strip() + "\n"
    return to, subj, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cc", default=None)
    ap.add_argument("--bcc", default=None)
    a = ap.parse_args()

    addr, pwd, host, port = load_creds(SECRETS)
    to, subj, body = parse_draft(Path(a.draft))
    sender_name = "if-water"

    msg = EmailMessage()
    msg["From"] = formataddr((sender_name, addr))
    msg["To"] = to
    if a.cc:
        msg["Cc"] = a.cc
    if a.bcc:
        msg["Bcc"] = a.bcc
    msg["Subject"] = subj
    msg["Message-ID"] = make_msgid(domain=addr.split("@")[-1])
    msg.set_content(body, charset="utf-8")

    print(f"发件人 : {sender_name} <{addr}>  via {host}:{port}")
    print(f"收件人 : {to}")
    print(f"主题   : {subj}")
    print(f"正文   : {len(body.split())} 词 / {len(body)} 字符")
    if a.dry_run:
        print("\n[dry-run] 未发送。去掉 --dry-run 即真发。")
        return

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) as s:
        s.login(addr, pwd)
        s.send_message(msg)
    print("\n✅ 已发送")


if __name__ == "__main__":
    main()
