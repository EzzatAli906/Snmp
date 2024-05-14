from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import logging
from pysnmp.smi import builder
from UPS_MIB import *
import re  # Import the regular expressions module
import psycopg2
from psycopg2 import Error

# Load the module
mibBuilder = builder.MibBuilder()

snmpEngine = engine.SnmpEngine()

TrapAgentAddress = '127.0.0.1'  # Trap listener address
Port = 162  # trap listener port

logging.basicConfig(filename='received_traps.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info("Agent is listening SNMP Trap on " + TrapAgentAddress + " , Port : " + str(Port))
logging.info('--------------------------------------------------------------------------')

print("Agent is listening SNMP Trap on " + TrapAgentAddress + " , Port : " + str(Port))

config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
)

# Configure community here
config.addV1System(snmpEngine, 'my-area', 'public')

# Initialize an empty array to store received traps
received_traps = []

# Connect to PostgreSQL
try:
    connection = psycopg2.connect(user="postgres",
                                  password="aa11ss22dd33",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="testdb")

    cursor = connection.cursor()

    # Print PostgreSQL Connection properties
    print(connection.get_dsn_parameters(), "\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if connection:
        cursor.close()

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    print("Received new Trap message")
    logging.info("Received new Trap message")

    trap_info = {}  # Initialize dictionary to store trap information

    for name, val in varBinds:
        trap_info[name.prettyPrint()] = val.prettyPrint()  # Store trap information in the dictionary
        logging.info('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

    received_traps.append(trap_info)  # Append the trap information dictionary to the main array

    # Create a new array to store the keys from each object in received_traps
    first_indexes = [list(trap.values())[1] for trap in received_traps]
    second_indexes = [tuple(map(int, index.split('.'))) for index in first_indexes]
    print(second_indexes)
    # Filter MIB data based on received indexes
    filtered_data = {}

    global_vars = dict(globals())
    for desired_mib_identifier in second_indexes:
        for object_name, object_value in global_vars.items():
            if isinstance(object_value, (MibScalar, MibTable, MibTableColumn, ObjectIdentity, MibIdentifier, ModuleCompliance, ObjectGroup, NotificationType)):
                if object_value.name[:len(desired_mib_identifier)] == desired_mib_identifier:
                    filtered_data[object_name] = object_value

    if filtered_data:
        print("Filtered data successfully:")
        for obj_name, obj_value in filtered_data.items():
            print(f"{obj_name}: {obj_value}")

            # Insert data into PostgreSQL table
            try:
                cursor = connection.cursor()
                postgres_insert_query = """ INSERT INTO traps (trap_desc, trap_oid, received_at) VALUES (%s,%s,now())"""
                record_to_insert = (obj_name, str(obj_value))
                cursor.execute(postgres_insert_query, record_to_insert)
                connection.commit()
                count = cursor.rowcount
                print(count, "Record inserted successfully into traps table")
            except (Exception, psycopg2.Error) as error:
                if connection:
                    print("Failed to insert record into traps table", error)
            finally:
                # closing database connection.
                if connection:
                    cursor.close()

    else:
        print("No data matching the desired MIB identifiers found.")

    # Function to get description based on object value and index

    logging.info("End of Incoming Trap")


ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise
