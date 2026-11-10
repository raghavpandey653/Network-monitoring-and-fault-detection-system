import sqlite3
connection = sqlite3.connect("network_monitor.db")
cursor = connection.cursor()
cursor.execute(""" CREATE TABLE IF NOT EXISTS monitoring_results(
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
                    status TEXT)
                    """)
connection.close()
