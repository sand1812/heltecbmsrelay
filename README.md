# heltecbmsrelay
Lib for Heltec BMS with external relays (same as QUCC bms)

Heltec's "Relay SMART BMS" is a kind of BMS with external relay (charge relay, discharge relay, pre-charge relay) rather than classic mosfet BMS.

This BMS is able to communicate via CAN, RS485 or bluetooth. Heltec doesn't provide any documentation for BT : only access is an android app called "AXE BMS" (not available on stores).

This python lib has been done by sniffing BT communications.

Lot of improvments to do, but it's working.

