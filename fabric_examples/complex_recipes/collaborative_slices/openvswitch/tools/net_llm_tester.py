import requests
import json
import re
import subprocess
import argparse
from typing import List, Dict, Any, Optional

def query_deepseek(prompt: str, model: str, host: str, port: str, stream: bool) -> str:
    """Sends a query to the DeepSeek model via Ollama API."""
    api_url = f"http://{host}:{port}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)}"

def parse_ping_output(ping_output: str) -> Dict[str, Dict[str, Any]]:
    """Parses the output of a ping command to extract RTT and packet loss statistics."""
    sections = ping_output.strip().split("PING ")
    results: Dict[str, Dict[str, Any]] = {}

    for section in sections[1:]:  # Skip first empty split
        lines = section.split("\n")

        # Extract destination IP
        first_line: str = lines[0]
        match = re.search(r'\((.*?)\)', first_line)
        if not match:
            continue
        dest_ip: str = match.group(1)

        # Extract RTT statistics
        rtt_line: Optional[str] = next((l for l in lines if "rtt min/avg/max/mdev" in l), None)
        if rtt_line:
            rtt_values = re.findall(r"[0-9]+\.[0-9]+", rtt_line)
            if len(rtt_values) == 4:
                min_rtt, avg_rtt, max_rtt, mdev_rtt = map(float, rtt_values)
            else:
                continue
        else:
            continue

        # Extract packet loss percentage
        packet_loss_line: Optional[str] = next((l for l in lines if "packet loss" in l), None)
        match = re.search(r'([0-9]+)% packet loss', packet_loss_line)
        packet_loss: int = int(match.group(1)) if match else 0

        results[dest_ip] = {
            "min_rtt": min_rtt,
            "avg_rtt": avg_rtt,
            "max_rtt": max_rtt,
            "mdev_rtt": mdev_rtt,
            "packet_loss": packet_loss
        }

    return results

def run_command(command: str) -> str:
    """Executes a shell command and returns its output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.stderr and "error" in result.stderr.lower():
            return f"Error: {result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Error executing {command}: {str(e)}"

def run_ping(dest_ips: List[str]) -> Dict[str, Dict[str, Any]]:
    """Runs ping tests and returns parsed results."""
    return {ip: parse_ping_output(run_command(f"ping -c 5 {ip}")) for ip in dest_ips}

def run_iperf(server_ip: str) -> Optional[Dict[str, Any]]:
    """Runs an iPerf3 test and parses the output."""
    iperf_output: str = run_command(f"export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib && iperf3 -c {server_ip} -P 4 -t 30 -i 10 -O 10")
    if "error" in iperf_output.lower():
        return None
    print(iperf_output)
    return parse_iperf3(iperf_output)

def run_mtr(dest_ips: List[str]) -> Dict[str, str]:
    """Runs MTR (My Traceroute) tests."""
    return {ip: run_command(f"mtr -r -c 10 {ip}") for ip in dest_ips}

def run_traceroute(dest_ips: List[str]) -> Dict[str, str]:
    """Runs traceroute tests."""
    return {ip: run_command(f"traceroute {ip}") for ip in dest_ips}

def parse_iperf3(iperf_text):
    parsed_data = {
        "source": "iperf3",  # Indicating the source of the data
        "server": {},
        "client": {"ports": []},
        "streams": [],
        "summary": {}
    }

    # Extract Server and Client Information
    server_match = re.search(r"Connecting to host ([\d\.]+), port (\d+)", iperf_text)
    if server_match:
        parsed_data["server"]["host"] = server_match.group(1)
        parsed_data["server"]["port"] = int(server_match.group(2))

    client_match = re.findall(r"\[ *\d+\] local ([\d\.]+) port (\d+) connected", iperf_text)
    if client_match:
        parsed_data["client"]["host"] = client_match[0][0]
        parsed_data["client"]["ports"] = [int(port) for _, port in client_match]

    # Extract individual stream data
    stream_data = {}
    stream_pattern = re.findall(
        r"\[\s*(\d+)\]\s+(\d+\.\d+)-(\d+\.\d+)\s+sec\s+([\d\.]+)\s+([KMG]Bytes)\s+([\d\.]+)\s+Mbits/sec\s+(\d+)?\s*([\d\.]+\s*[KMG]?Bytes)?",
        iperf_text
    )

    for match in stream_pattern:
        stream_id = int(match[0])
        interval = {"start": float(match[1]), "end": float(match[2])}
        transfer = f"{match[3]} {match[4]}"
        bitrate = f"{match[5]} Mbits/sec"
        retransmissions = int(match[6]) if match[6] else 0
        cwnd = match[7].strip() if match[7] else None

        if stream_id not in stream_data:
            stream_data[stream_id] = {"id": stream_id, "intervals": [], "total": {"transfer": "", "bitrate": "", "retransmissions": 0}}

        stream_data[stream_id]["intervals"].append({
            "start": interval["start"],
            "end": interval["end"],
            "transfer": transfer,
            "bitrate": bitrate,
            "retransmissions": retransmissions,
            "cwnd": cwnd
        })

    # Extract total summary
    summary_match = re.findall(
        r"\[SUM\]\s+(\d+\.\d+)-(\d+\.\d+)\s+sec\s+([\d\.]+)\s+([KMG]Bytes)\s+([\d\.]+)\s+Mbits/sec\s+(\d+)?",
        iperf_text
    )
    if summary_match:
        last_summary = summary_match[-1]
        parsed_data["summary"] = {
            "total_duration": float(last_summary[1]),
            "total_transfer": f"{last_summary[2]} {last_summary[3]}",
            "total_bitrate": f"{last_summary[4]} Mbits/sec",
            "total_retransmissions": int(last_summary[5]) if last_summary[5] else 0
        }

    # Collect stream results
    parsed_data["streams"] = list(stream_data.values())

    return parsed_data

def main(dest_ips: List[str], ollama_model: str, ollama_host: str, ollama_port: str, stream: bool, test_type: str) -> None:
    """Runs network tests and sends results to the LLM for analysis."""
    results: Optional[Dict[str, Any]] = {}

    if test_type == "ping":
        results = run_ping(dest_ips)
    elif test_type == "iperf":
        results = run_iperf(dest_ips[0])
    elif test_type == "mtr":
        results = run_mtr(dest_ips)
    elif test_type == "traceroute":
        results = run_traceroute(dest_ips)

    # Print and send results to the LLM for analysis
    print("Test Results:", json.dumps(results, indent=4))
    if results is None:
        print("Test execution failed!")
        return
    
    query: str = f"Analyze this network test result: {json.dumps(results, indent=4)}"
    response: str = query_deepseek(query, ollama_model, ollama_host, ollama_port, stream)
    print("\nLLM Analysis Response:", response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run network tests and analyze results with an LLM.")
    parser.add_argument("--dest_ips", nargs='+', required=True, help="List of destination IPs.")
    parser.add_argument("--ollama_model", type=str, required=True, help="Ollama model name.")
    parser.add_argument("--ollama_host", type=str, required=True, help="Ollama API host.")
    parser.add_argument("--ollama_port", type=str, required=True, help="Ollama API port.")
    parser.add_argument("--stream", action='store_true', help="Enable streaming mode.")
    parser.add_argument("--test_type", type=str, choices=["ping", "iperf", "mtr", "traceroute"], required=True, help="Type of network test.")

    args = parser.parse_args()
    main(args.dest_ips, args.ollama_model, args.ollama_host, args.ollama_port, args.stream, args.test_type)
