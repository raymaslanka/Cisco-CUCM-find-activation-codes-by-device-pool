# Cisco-CUCM-find-activation-codes-by-device-pool
Cisco CUCM: Find phone activation codes by device pool

Cisco CUCM version 12.5 introduced the ability for users to provision phones using activation codes.  Currently when exporting activation codes from the admininstrative interface the values include Device Name,	Device Desc,	User ID,	Activation Code, and Expiry. 

The challenge in larger rollouts may be that there is no way to sort the codes by location.

This is a sample of how to use two CUCM AXL requests to filter the list of activation codes by device pool, supplying a list of the codes associated with only one device pool in question. 
