# Snmp
SNMP is a protocol used for network management and monitoring of devices within a network. It facilitates the exchange of management information between network devices, allowing administrators to monitor device performance, detect and troubleshoot network problems, and manage network configurations remotely.

***compiling mibs***
we use lib called mibdump.py
here is the command we use to compile mib file

vote>we should have all dependent mibs in the same path 


mibdump.py --destination-directory=path/to/compiled/mib --mib-source=http://mibs.snmplabs.com/asn1/@mib@ --debug all path/to/mibfile.mib



***input sample***

This SNMP script is designed to parse compiled MIB (Management Information Base) files as input, extracting specific information, such as issue names or descriptions, using Object Identifiers (OIDs). By leveraging OIDs, the script retrieves precise data points defined within the MIB structure

trap sample >> sudo snmptrap -c public -v 2c 127.0.0.1 "" 1.3.6.1.2.1.43.18.2.0.1


****output sample***

The output from this SNMP script is formatted for readability, presenting the extracted data in a structured format, including the date and alarm name. The parsed information is seamlessly integrated into a designated database table immediately after extraction from the MIB file


***note***
to run this script you have to put mib.py in the same script path 
and you must create sql database table 
\\\\\\\\\\\\\\\\\\\\\\\\
CREATE TABLE traps (
    id SERIAL PRIMARY KEY,
    trap_oid TEXT NOT NULL,
    trap_value TEXT NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
\\\\\\\\\\\\\\\\\\
    (user="postgres",
     password="aa11ss22dd33",
    host="127.0.0.1",
    port="5432",
    database="testdb")
                                
