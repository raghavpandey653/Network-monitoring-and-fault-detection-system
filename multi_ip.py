import ipaddress
import subprocess
import sqlite3
connection =sqlite3.connect("network_monitor.db")
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS monitoring_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    sent_packets INTEGER,
    received_packets INTEGER,
    lost_packets INTEGER,
    packet_loss REAL,
    min_rtt INTEGER,
    max_rtt INTEGER,
    avg_rtt INTEGER,
    avg_jitter REAL,
    status TEXT
    )
""")
connection.commit()
cursor.execute("PRAGMA table_info(monitoring_results)")
columns = [column[1] for column in cursor.fetchall()]
if "status" not in columns:
    cursor.execute(
        "ALTER TABLE monitoring_results ADD COLUMN status TEXT"
    )
    connection.commit()
ip_addresses = ["8.8.8.8", "1.1.1.1"]
for ip in ip_addresses:
    try:
        ip=ipaddress.ip_address(ip)
        result=subprocess.run(
            ["ping", "-n", "5", str(ip)],
            capture_output=True,
            text=True,
            timeout=10
            )
        ping_output = result.stdout
        minimum_rtt = None
        maximum_rtt = None
        average_rtt = None
        average_jitter = None
        lines = ping_output.splitlines()
        rtt_values=[]
        for line in lines:
             if "time=" not in line:
                  continue
             rtt_value=int(line.split("time=")[1].split("ms")[0])
             rtt_values.append(rtt_value)     
        print(f"RTT values: {rtt_values}")
        jitter_values=[]
        if len(rtt_values) < 2:
            print("Insufficient RTT data for jitter calculation")
        else:
            for i in range(len(rtt_values) - 1):
                difference=abs(rtt_values[i+1]-rtt_values[i])
                jitter_values.append(difference)
            average_jitter = sum(jitter_values) / len(jitter_values)
            print(f"Average jitter: {average_jitter: .2f}")
        sent_packets = int(ping_output.split("Sent = ")[1].split(",")[0])
        received_packets = int(ping_output.split("Received = ")[1].split(",")[0])
        lost_packets = int(ping_output.split("Lost = ")[1].split(" (")[0])
        print(f"Sent packets: {sent_packets}")
        print(f"Received packets: {received_packets}")
        print(f"lost packets: {lost_packets}")
        if sent_packets <= 0 or received_packets < 0 or received_packets > sent_packets:
            print("Invalid packet count")
        else:
            lost_packets = sent_packets - received_packets
            loss_percentage = lost_packets / sent_packets * 100
            print(f"Packet loss: {loss_percentage}")
            if loss_percentage == 0:
                 status = "ONLINE"
            elif loss_percentage == 100:
                 status = "UNREACHABLE"
            else:
                 status = "DEGRADED"
            print(f"status: {status}")
        if "Minimum = " in ping_output:
            minimum_rtt = int(ping_output.split("Minimum = ")[1].split("ms")[0])
            maximum_rtt = int(ping_output.split("Maximum = ")[1].split("ms")[0])
            average_rtt = int(ping_output.split("Average = ")[1].split("ms")[0])
            print(f"minimun rtt: {minimum_rtt}")
            print(f"maximun rtt: {maximum_rtt}")
            print(f"average rtt: {average_rtt}")
        else:
            print("RTT data unavailable")
        cursor.execute(
        """INSERT INTO monitoring_results
        (ip_address, sent_packets, received_packets, lost_packets,
        packet_loss, min_rtt, max_rtt, avg_rtt, avg_jitter, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (str(ip), sent_packets, received_packets, lost_packets,
        loss_percentage, minimum_rtt, maximum_rtt, average_rtt,
        average_jitter, status)
                )
        connection.commit()
        print(ping_output)
        print("Monitoring:", ip)
    except ValueError:
            print("Invalid IP, skipping...")
            continue
    except subprocess.TimeoutExpired:
         print("subprocess timed out")
         continue