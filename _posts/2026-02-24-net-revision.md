---
layout: post
title: profcane's networking revision
date: 2026-02-20 05:40:00 +0800
---
<style>
  
  .quiz-options {
    list-style: none;
    padding: 0;
    margin-top: 15px;
  }

  .option {
    padding: 10px 15px;
    margin-bottom: 8px;
    cursor: pointer;
    border: 1px solid gray;
    transition: all 0.2s ease;
    user-select: none;
  }

  .option:hover:not(.selected) {
    border: 1px solid white;
  }

  .option.selected {
    border: 1px solid #458588;
    background-color: #1d2021;
  }

  .submit-btn {
    margin-top: 10px;
    padding: 8px 18px;
    cursor: pointer;
    background: none;
    border: 1px solid gray;
    color: inherit;
    font: inherit;
    transition: border-color 0.2s;
  }

  .submit-btn:hover {
    border-color: white;
  }

  .quiz-block.answered .option {
    cursor: default;
    pointer-events: none;
  }

  .quiz-block.answered .submit-btn {
    display: none;
  }

  .quiz-block.answered .option.correct {
    background-color: #1c1c1c;
    color: green;
    font-weight: bold;
  }

  .quiz-block.answered .option.selected.correct {
    background-color: #1c1c1c;
    color: green;
    font-weight: bold;
  }

  .quiz-block.answered .option.selected:not(.correct) {
    color: #cc241d;
    opacity: 0.9;
  }

  .quiz-block.answered .option:not(.correct):not(.selected) {
    color: #86181d;
    opacity: 0.7;
  }

  .explanation {
    display: none;
    margin-top: 25px;
    padding-inline: 15px;
    border-left: 2px solid #b8bb26;
  }

  .quiz-block.answered .explanation {
    display: block;
    animation: fadeIn 0.5s;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .multi-label {
    font-size: 0.8em;
    color: #928374;
    margin-top: 8px;
    margin-bottom: -4px;
  }

#score-container {
    background: #282828;
    border: 1px solid #458588;
    padding: 15px;
    border-radius: 8px;
    z-index: 1000;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    font-family: monospace;
  }

  .score-val {
    color: #b8bb26;
    font-weight: bold;
    font-size: 1.2em;
  }

</style>

[recommended listening for this post is do it (yves remix)](https://www.youtube.com/watch?v=kvhVECfGsw8)

NB: multi-select means none, any, or all are true :)

![meow](https://i.imgur.com/Fu1lazS.png)

<div class="quiz-block" markdown="1">
### question 1

![network topo](https://i.imgur.com/Al4m38h.png)

consider the following setup. i have setup the trunk between `S1` and `S2`, VLAN 10 on `G1/0/6 S1` and `G1/0/11 S2`, and VLAN 20 on `G1/0/18` as per the diagram i have also correctly set the router's ip addresses on their interfaces. pc A can ping pc B, but no pcs can ping the router. this is because

<ul class="quiz-options">
  <li class="option">STP detects a loop between the router and switches and shuts the network down.</li>
  <li class="option correct">the connections R1-S1 and R2-S2 also need VLANs configured.</li>
  <li class="option">nothing is wrong with the configuration as described, it is most likely a physical layer issue.</li>
  <li class="option">if the trunk was configured without explicitly stating which VLANs are allowed, the default option is to only allow VLAN 1, hence neither VLAN can actually use the trunk.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown=1>
<b>explanation</b> STP does not come into play here, and the default for a trunk is to allow <i>all</i> VLANs. the default for an interface on a switch is ONLY VLAN 1, so the switch cannot send packets from PC A to R1 (the VLAN has not been properly configured). 
</div>

</div>
<hr>

<!-- QUESTION 2 -->
<div class="quiz-block" markdown="1">
### question 2

which of these is possible to do on a CISCO router?

<ul class="quiz-options">
  <li class="option">setting multiple VLANs on a LAN subinterface</li>
  <li class="option">setting an IP address on a LAN subinterface before its VLAN is configured</li>
  <li class="option correct">setting a VLAN on a LAN subinterface before its IP address is configured</li>
  <li class="option">all of these are possible</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown=1>
<b>explanation</b> one VLAN+IP address per LAN subinterface. the key thing here is that an IP address is 'more specific' than a VLAN, and the router requires you to set the VLAN (with the `encapsulation dot1q ..`) command before configuring the IP address. (you'll note that in each example in the labs, the `encapsulation` command is performed before setting the IP).
</div>
</div>

<hr>
<div class="quiz-block" markdown="1">
### question 3

LAN subinterface `G0/0/1.10` is currently configured to `192.168.1.10/24`. i want to configure LAN subinterface `G0/0/1.20` - which address + subnet mask would the router let me configure it to?

<ul class="quiz-options">
  <li class="option">192.168.1.3 255.255.255.252</li>
  <li class="option">192.168.1.24 255.255.255.0</li>
  <li class="option correct">192.168.2.1 255.255.254.0</li>
  <li class="option">192.168.1.14 255.255.255.254</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> the only constraint that the router enforces is that no subinterface must overlap (when it receives a packet destined for a specific subnet, it _must_ know which interface to send it to, there cannot be any 'ambiguities'). for each IP address above starting with `192.168.1.x`, the `192.168.1.10/24` will necessarily overlap (because that subnet covers every single `192.168.1.x` addr). `192.168.2.0 255.255.254.0` covers from `192.168.2.0 - 192.168.3.255`, hence no overlap.
</div>
</div>
<hr>

<!-- QUESTION 4 -->
<div class="quiz-block" markdown="1">
### question 4

LAN subinterface `g1/0/1.10` is currently configured to `192.168.1.10/28`. i want to configure LAN subinterface `g1/0/1.20`. which address would i be able to configure it to?

<ul class="quiz-options">
  <li class="option">192.168.1.3 | 255.255.255.252</li>
  <li class="option">192.168.1.24 | 255.255.255.0</li>
  <li class="option">192.168.1.14 | 255.255.255.254</li>
  <li class="option correct">192.168.2.0 | 255.255.254.0</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> the rule is no overlapping subnets. `192.168.1.10/28` covers `192.168.1.0–192.168.1.15`. option A (`192.168.1.3/30`) covers `192.168.1.0–192.168.1.3` - overlap. option B (`192.168.1.24/24`) covers all of `192.168.1.x` - overlap. option C (`192.168.1.14/31`) covers `192.168.1.14–192.168.1.15` - overlap. option D (`192.168.2.0/255.255.254.0`) covers `192.168.2.0–192.168.3.255` - no overlap, so this is valid.
</div>
</div>
<hr>

<!-- QUESTION 5 -->
<div class="quiz-block" markdown="1">
### question 5

![network topo](https://www.ciscopress.com/content/images/chap4_9780136729358/elementLinks/04fig05_alt.jpg)

consider the network topology, noting that `PC1` and `PC2` are on separate VLANs. `PC1` sends `PC2` an ICMP ping request. assuming that all ARP tables are empty, which of the following is true?

<ul class="quiz-options">
  <li class="option">from S2 to PC2, the packet has a VLAN tag.</li>
  <li class="option">the source MAC address of the packet stays constant throughout the entire lifecycle of the packet.</li>
  <li class="option">when S2 forwards the packet to PC2, it will add PC2's MAC address to its MAC address table.</li>
  <li class="option correct">the packet starts with no VLAN tag, then S1 adds one, then R1 removes and adds another one, then S2 finally removes it.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown=1>
<b>explanation:</b> PCs are 'VLAN unaware', the PC only sends an ethernet packet. VLAN tags are a layer 2 thing, so they are mainly dealt with by switches (as well as layer 3 routers, which need to decapsulate the packet to check its IP, then reapply the next VLAN tag during encapsulation). switches only learn MAC addresses from _source_ MAC addresses and not destinations, and when the router decapsulates the packet, it modifies the source MAC address of the packet to be the router's.
</div>
</div>
<hr>

<!-- QUESTION 6 -->
<div class="quiz-block" markdown="1">
### question 6

same setup as above - `PC1` wants to send an inter-VLAN ICMP ping to `PC2`. assume all ARP, MAC address, and routing tables are empty. which of the following is true?

<ul class="quiz-options">
  <li class="option">PC1 will first send an ARP request to PC2 to know which MAC address to send its ICMP packet to.</li>
  <li class="option correct">PC2 will eventually send an ARP response addressed to R1.</li>
  <li class="option">when S1 receives an ARP request, it will flood it out of all 3 ports.</li>
  <li class="option">three ARP requests are sent throughout the process of sending the ICMP request.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown=1>
<b>explanation:</b> PC1 cannot send an ARP request to PC2 because they are on different subnets! PC1 would send it to the default gateway (the router), and the router would _then send its own ARP request_ to PC2, and PC2 would respond. throughout this process only two ARP requests would be sent (PC1 would need to ARP for its default gateway, and the router would need to ARP for PC2). third option is wrong because a switch floods a broadcast packet out of all ports _except_ ingress, so it would only send 2 packets max (if that).
</div>
</div>
<hr>

<!-- QUESTION 7 -->
<div class="quiz-block" markdown="1">
### question 7

![network topo](https://i.imgur.com/BKFIc1c.png)

`H1`, `H2`, `H3` are on subnet A, and `H4`, `H5`, `H6` are on subnet B. all six are connected to a single unconfigured switch with no VLANs, and all ARP tables are empty. which of the following is true?

<ul class="quiz-options">
  <li class="option">if H1 tries to ping H4, H1 will try to send an ARP request to H4, which will not get resolved.</li>
  <li class="option correct">if H1 tries to ping H2, the switch will flood by sending 5 packets.</li>
  <li class="option">if H1 tries to ping H2, the switch will learn H2's MAC address (before H2 responds) by reading the destination MAC address.</li>
  <li class="option">all hosts will be able to ping one another.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> option A is wrong - H1 won't ARP for H4 directly because H4 is on a different subnet. H1 would instead try to send to its default gateway (but there is none here, so the ping just fails). option B is correct - the switch floods the ARP broadcast out of all ports except the ingress port, which is 5 ports. option C is wrong  switches only learn MAC addresses by reading _source_ MAC addresses, not destination. option D is wrong - different subnets require a routing-capable device, which doesn't exist here.
</div>
</div>
<hr>

<!-- QUESTION 8 -->
<div class="quiz-block" markdown="1">
### question 8

i have connected ports g1/1-2 together on DSW1 and S1, and i want to configure etherchannels. which of the following is true? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">on DSW1's side i configure it as desirable, and on S1 i configure as auto. i wait until the port channel initiates, then i switch DSW1 to auto. the port channel remains up.</li>
  <li class="option correct">on DSW1's side i configure it as active, and on S1's side i configure it as passive. an etherchannel successfully forms.</li>
  <li class="option">on DSW1's side i configure it as desirable, and on S1's side i configure it as passive. an etherchannel successfully forms.</li>
  <li class="option">on DSW1's side i configure it as desirable, and on S1's side i configure it as on. an etherchannel successfully forms.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown=1>
<b>explanation:</b> desirable / auto are for PAGP while active / passive are for LACP, mixing the two results in an etherchannel not forming. for `on` to work both sides need to be `on`, and at least one needs to be active / desirable in other for the channel to form
</div>
</div>
<hr>

<!-- QUESTION 9 -->
<div class="quiz-block" markdown="1">
### question 9 - rstp

consider the diagram below, where `A` is elected as the root bridge, all links have default cost, and all ports and switches have default priority. `G1` on switch `C` is elected as the root port. which of the following describes a correct pattern of cause and effect?

![rstp diagram](https://i.imgur.com/okSrCaB.png)

<ul class="quiz-options">
  <li class="option">if an etherchannel is formed with ports G1 and G2 on both A and C, G2 will remain as an alternate port.</li>
  <li class="option correct">if port G2 on switch A is configured with priority 16, port G2 on switch C will be elected as the root port.</li>
  <li class="option">if port G3 on B and port G4 on A are configured with cost 50 each, port G3 on C will be elected as the root port as the total cost is now 100.</li>
  <li class="option">if the link between both G4 ports are severed, C is re-elected as the root bridge.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> option A is wrong, an etherchannel bundles the two separate links into one single connection and is generally treated as a single connection throughout _all_ protocols RSTP included. B is correct, port G2 on switch C will receive a BPDU w/ a lower port priority and switch C will pick that instead. C is wrong bc cost only matters on _egress_ ports (if it was port G3 on C and port G4 on B, then the new cost would b calculated). D wrong because root bridge election is based on lowest BID and BID is not affected by any link severing
</div>
</div>
<hr>

<!-- QUESTION 10 -->
<div class="quiz-block" markdown="1">
### question 10

select the true statements about RSTP. (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">it is possible for both ends of a link connecting two switches to be designated ports.</li>
  <li class="option correct">switches will continue to send BPDUs to one another even after RSTP is fully negotiated.</li>
  <li class="option">20000 is a valid bridge priority value.</li>
  <li class="option correct">a port that is Alternate can still receive packets, but they are dropped immediately after being received.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> A wrong, two ports on the end of the same link cant have the same role, B correct they will keep sending BPDUs, C wrong as bridge priority must be multiple of 4096, D correct (it receives BPDUs) & drops data frames 
</div>
</div>
<hr>

<!-- QUESTION 11 -->
<div class="quiz-block" markdown="1">
### question 11 - hsrp

select the correct statements about HSRP. (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">if R1 and R2 are configured with the same priority, the active router is randomly selected.</li>
  <li class="option">if preempt is not configured, the passive router will not take over the active router when the active router goes down.</li>
  <li class="option correct">it is not immediate for the passive router to take over the active router, as it must wait for multiple expected hello packets to not arrive.</li>
  <li class="option correct">if R1 and R2 are configured for HSRP on two VLANs 10 and 20, and the link connecting the two routers is a trunk w/ native vlan 1, the hello packets must have VLAN tags.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> option A wrong as the active router is selected deterministically through highest IP addr. option B wrong, the purpose of preempt is for the higher priority router to _take Back_ the status of active router when it comes back online, option C correct option D correct
</div>
</div>
<hr>

<!-- QUESTION 12 -->
<div class="quiz-block" markdown="1">
### question 12

`PC1` sends an ARP request for its default gateway (a virtual HSRP address shared by R1 and R2). which of the following is true?

<ul class="quiz-options">
  <li class="option">the request's destination MAC address is PC1's, and its source MAC address is the broadcast address.</li>
  <li class="option">the reply's destination MAC address is PC1's, and its source MAC address is the active router's physical MAC address.</li>
  <li class="option">the request's source MAC address is neither R1's nor R2's MAC address.</li>
  <li class="option correct">the reply's source MAC address is neither R1's nor R2's MAC address.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> the request destination MAC address is the broadcast and the source MAC address is PC1, the reply destination MAC address is PC1 and the source mac address is the virtual MAC addr for HSRP
</div>
</div>
<hr>

<!-- QUESTION 13 -->
<div class="quiz-block" markdown="1">
### question 13 - ospf

![ospf topology](https://i.imgur.com/BsCs7om.png)

the following topology is set up for OSPF (R1, R2, DSW1 are all L3 devices; PC-A is off R1, PC-B is off R2, PC-C is off DSW1). which of the following is true? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">there will be one DR, one BDR, and one DROTHER among R1, R2, and DSW1.</li>
  <li class="option">R1 will have 2 neighbors; R2 and DSW1 will each have 1 neighbor, as OSPF is non-looping.</li>
  <li class="option">the shortest paths to each device are calculated on one L3 device and then distributed to all others.</li>
  <li class="option">if the default cost is 1 and DSW1 G1/0/2's cost is set to 10, the cost of the route from DSW1 to R2 is 3.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> given that the routers are all on point to point links, they dont actly share a broadcast segment, and broadcast segments are where the whole DR / BDR / DROTHER thing comes in. there wont be a single DROTHER across the L3 devices, A is therefore wrong. B is wrong if u understand OSPF even remotely, C is wrong because shortest paths are calculated _per_ device, and D is wrong bc cost applies to egress ports, of which there are 2 (DSW1 G1/0/1 + R1 G0/0/0) therefore cost is 2.

</div>
</div>
<hr>

<!-- QUESTION 14 -->
<div class="quiz-block" markdown="1">
### question 14

![topo](https://i.imgur.com/yJ3vyV8.png)

consider this topology. router A and D both have loopback addresses and routes configured for `44.44.44.44`, and B is the PC's default gateway. A, B, C, and D are all advertising their routes to one another via OSPF. which of the following is true? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">B will prefer to route packets to A, because it is nearer in terms of hops (and therefore costs less in OSPF).</li>
  <li class="option correct">if A or D shuts down (but not both), PC A will still be able to ping 44.44.44.44.</li>
  <li class="option">each router will have one neighbor designated DR, another designated BDR, and another designated DROTHER.</li>
  <li class="option">the ports on both ends of the link connecting the two switches will both be root ports.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> option A wrong (very tricky option! note this one specifically, bc switches are L2 devices and OSPF is a l3 protocol it does _not_ factor in switches at all). option B is correct because if A shuts down then LSAs will be re-sent and LSDBs will re-update and reflect D as the only route for 44.44.44.44 & vice-versa, C is wrong because there will be one DR and the DR cannot have a DR as its neighbor, D wrong because of reason mentioned above (can be root | alternate, root | designated, designated | alternate, _never_ root | root)
</div>
</div>
<hr>

<!-- QUESTION 15 -->
<div class="quiz-block" markdown="1">
### question 15

![topo](https://i.imgur.com/WXiSFA5.png)

i do `show spanning-tree` on S2 in a topology where S1 connects to S2 via G1/0/1 and G1/0/2, and S2 connects onward to the root via G1/0/3. the output is:

```
G1/0/1 | DESG | FWD | cost 20000 | priority 128.1
G1/0/2 | DESG | FWD | cost 20000 | priority 16.2
G1/0/3 | ???? | FWD | cost 20000 | priority 128.3
```

which of the following is true? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">G1/0/3 will be a designated port.</li>
  <li class="option">given that S2 G1/0/2's priority is lower, S1 G1/0/2 is guaranteed to be the root port on S1.</li>
  <li class="option correct">the BID on the BPDUs received by S1 on both G1/0/1 and G1/0/2 will be identical.</li>
  <li class="option correct">if G1/0/1 and G1/0/2 are configured as an etherchannel, RSTP will treat S1 as if it only has one connection to S2.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> A wrong as G1/0/3 shld be a root port. B wrong bc 'guaranteed', root ports are elected via _cost_ first and foremost (which is first dictated by bandwidths), so if the cable is a lower bandwidth the cost will be higher (this is a bit tricky + annoyingly phrased but :P), C correct bc BID is device-specific and theyre both receiving from the same device, D correct bc RSTP treats etherchanneled interfaces as js one interface
</div>
</div>
<hr>

<!-- QUESTION 16 -->
<div class="quiz-block" markdown="1">
### question 16 - dhcp

![topo](https://imgur.com/DfDGo0O.png)

consider a topology where a router is configured as a DHCP server, and PCs are on a different subnet. the connection from SW1 to DSW2 is VLAN 1 (default). which of the following is true? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">PC A runs `ipconfig /release`, then `ipconfig /renew`. the DHCP Discover is addressed to its default gateway.</li>
  <li class="option correct">ip helper-address [DHCP router IP] should be configured on DSW2's interface facing the PCs.</li>
  <li class="option correct">one of the excluded addresses should be the PC's default gateway.</li>
  <li class="option">the DHCP router does not need to know the route back to the PC's subnet - it will send packets back to DSW2 anyway.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> A wrong, Discover is always addressed to broadcast addr (note that if a device is even sending Discover it doesnt _have_ a default gateway yet), B correct, C correct, D no (if DHCP not working this is a common reason as to why, either configure OSPF or set static route, DHCP will need to address to the _helper-address_ interface and it doesnt _know_ where it is right off the bat)
</div>
</div>
<hr>

<!-- QUESTION 17 -->
<div class="quiz-block" markdown="1">
### question 17

which of the following statements about DHCP is true? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option">the client IP address field (`ciaddr`) in a Request is always 0.0.0.0, as a PC typically only requests a new DHCP address if it does not already have one.</li>
  <li class="option">after the PC receives the Offer, it immediately updates its NIC to use the new IP.</li>
  <li class="option">once a DHCP Relay device receives an Offer from the DHCP server, it will populate the Offer's `giaddr` field with its own IP address.</li>
  <li class="option">if the DHCP server has multiple pools, it always uses the Discover packet's `giaddr` field to determine which pool to use.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> option A wrong because it can request when it needs to renew before the lease expires, option B wrong because NIC is typically only updated after ACK is received, C is wrong because DHCP Relay populates _giaddr_ when Discover is sent. D wrong because it might also use the interface IP addr (assume a situation wherein there is no Relay, therefore giaddr remains blank)
</div>
</div>
<hr>

<!-- QUESTION 18 -->
<div class="quiz-block" markdown="1">
### question 18

![topo](https://i.imgur.com/4PA8Fbp.png)

consider a topology where a DHCP router services both VLAN 10 and VLAN 20. trunking is configured to allow all VLANs, and the DSWs have negotiated HSRP - one DSW is active for VLAN 10, the other for VLAN 20. both DSWs are configured as DHCP relay agents. which of the following is true? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option correct">ip helper-address is to be configured on the VLAN interfaces of both DSWs.</li>
  <li class="option correct">HSRP hellos will be flooded out of the trunk ports (G1/0/2 and G1/0/1), in addition to other interfaces.</li>
  <li class="option correct">if a device on VLAN 10 sends a Discover, the DHCP router may receive two different DHCP requests - one from each DSW.</li>
  <li class="option">if the DHCP's IP addresses are all within VLAN 10, no VLAN 10 device can get a DHCP IP address, as the PC will attempt to ARP for the DHCP router and fail.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> option A correct, option B correct (HSRP hellos flooded out of all interfaces that support the VLAN), option C correct (consider the situation where the switch does not have a populated ARP table and the first packet it receives is a Discover, addressed to Broadcast. the switch will flood the Broadcast out, meaning it gets sent to both DSWs, which _both_ fulfill their roles as Relays. in this scenario the DHCP server will sort it out - depends on implementation, but DHCP will end being fulfilled regardless). D wrong because of the exact same reason, Discovers are addressed to Broadcast. ordinarily if the PC tried to ARP _for_ the DHCP router, it will fuck up and not resolve, but in this case its actually completely fine) 
</div>
</div>
<hr>

<!-- QUESTION 19 -->
<div class="quiz-block" markdown="1">
### question 19

select the true statements about OSPF. (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option correct">if a directly connected interface link is shut down, OSPF will stop advertising it and it will eventually be removed from all participating routers' LSDBs.</li>
  <li class="option correct">if the OSPF adjacency state between two DROTHERs is 2-WAY, OSPF is working as intended.</li>
  <li class="option">if the OSPF adjacency state between a DR and a BDR is EXSTART and has remained there for around a minute, OSPF is working as intended.</li>
  <li class="option">to advertise a loopback interface on OSPF for the IP address 100.100.100.100/24, the command is `network 100.100.100.100 255.255.255.0 area [AREA-ID]`.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> option 1 correct, option 2 correct (2-WAY is the expected connection), option 3 wrong bc EXSTART should be finished within a few seconds, if EXSTART is still ongoing after a long period of time then it indicates there is a mismatch in the HELLOs that prevents a full adjacency from forming. option 4 wrong bc it should be a wildcard mask.
</div>
</div>
<hr>

<hr>

<!-- QUESTION 20 -->
<div class="quiz-block" markdown="1">
### question 20 — NAT

![nat topology](https://i.imgur.com/eTFftwr.png)

`R2` is configured with NAT for the internal IP range of `192.168.10.0/23`. assume a point-to-point connection from R2 to the ISP Edge Router on `172.17.0.1/30`. which of the following is true?

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option correct">ping 8.8.8.8 sent from R2 will not work because R2 is not configured to translate its own IP address.</li>
  <li class="option">the correct command to create the access-list is <code>access-list 1 permit 192.168.10.0 255.255.254.0</code>.</li>
  <li class="option">if PC2 is hosting a webserver which must always remain accessible from the internet, using pooled NAT is the best choice.</li>
  <li class="option">if the internal 10.1.1.0/30 path is not configured w/ its own access list and NAT pool, the PCs will not be able to access the internet.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> if uve experimented with NAT in the labs you will know that A is wrong, when the PCs send a ping the router is able to translate the source to a public addr which the internet is able to handle, however when the router sends a ping it does not translate the source IP addr to a public addr hence it is dropped. B is wrong, access-lists require wildcard masks. C is clearly wrong because u want a static config. D is wrong because u dont rlly need to NAT that interface for it to matter, PC A will forward to default gateway (R1), R1 will route to R2, R2 will NAT the source ip addr (which has always been PC A's addr) and everything is fine
</div>
</div>
<hr>

<!-- QUESTION 21 -->
<div class="quiz-block" markdown="1">
### question 21

on a topology with NAT configured, i run `show ip nat translations` on the NAT-enabled router and no translations are shown. which of the following is a potential reason as to why? (select all that apply)

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option correct">a routing issue is preventing end-users from even reaching the NAT router.</li>
  <li class="option correct"><code>ip nat outside</code> and <code>ip nat inside</code> are not properly configured on the correct interfaces.</li>
  <li class="option correct">the access-list does not correctly cover the addresses of end users.</li>
  <li class="option">ISP issue.</li>
</ul>
<button class="submit-btn">submit</button>

<div class="explanation" markdown="1">
<b>explanation:</b> only one wrong is the ISP issue, because even if the ISP was wrong packets would still hit the NAT router and trigger a translation. everything else would prevent a successful firing of NAT.
</div>
</div>

<hr>

<!-- QUESTION 22 -->
<div class="quiz-block" markdown="1">
## question 22

which of the following is true for NAT?

<p class="multi-label">multi-select</p>
<ul class="quiz-options">
  <li class="option correct">assuming PAT overload with a pool of 3 available public IP addresses, the _theoretical_ limit for number of concurrently supportable hosts is 65536 * 3.</li>
  <li class="option">_inside global_ denotes the translated private IP address of a publicly accessible host.</li>
  <li class="option">for a statically configured IP address for a webserver, the NAT translation exists in the router's table for as long as the webserver remains up.</li>
  <li class="option">a PC pings youtube.com successfully. assuming dynamic, pooled NAT, the router translates its IP exactly once.</li>
</ul>

<button class="submit-btn">submit</button>


<div class="explanation" markdown="1">
<b>explanation: </b> there are 65536 possible ports so yes the theoretical limit is 65536 ports per available IP address. _inside global_ denotes the public IP address of the host within ur internal private network. static NAT translation remains permanently up regardless of whether or not the webserver goes down. further note that if it was a dynamic assignment, the assignment wld only exist for a brief period of time (so in no scenario is option C ever correct, actually). an address is translated exactly twice: once going in, once going out.
</div>
</div>
<hr>

<!-- QUESTION 23 -->
<div class="quiz-block" markdown="1">
## question 23

a PC attempts to access www.youtube.com. assume that it has a caching server on its private network which it is configured to use, and additionally assume the server is completely blank. which of the following is a true statement about the process of DNS resolution?

<ul class="quiz-options">
  <li class="option">the DNS server asks its root server, which asks the .com DNS server, which asks the authoritative source for youtube.com. </li>
  <li class="option correct">the DNS server asks its root server, which returns a list of nameserver records to sources for .com.</li> 
  <li class="option">the DNS server asks the authoritative source for youtube.com immediately.</li>
  <li class="option">the DNS server asks its root server, which returns the IP address for youtube.com immediately.</li>
</ul>

<button class="submit-btn">submit</button>


<div class="explanation" markdown="1">
<b>explanation: </b>too tired to write just take my word for it
</div>
</div>
<hr>

<div id="score-container">
  Score: <span id="current-score" class="score-val">0</span> / <span id="max-score">0</span> (will update per qn answered)
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  let totalScore = 0;
  const quizBlocks = document.querySelectorAll('.quiz-block');
  
  const scoreDisplay = document.getElementById('current-score');
  const maxDisplay = document.getElementById('max-score');

  maxDisplay.textContent = quizBlocks.length;

  quizBlocks.forEach(function(block) {
    const options = block.querySelectorAll('.option');
    const submitBtn = block.querySelector('.submit-btn');
    const isMulti = block.querySelector('.multi-label') !== null;

    options.forEach(function(option) {
      option.addEventListener('click', function() {
        if (block.classList.contains('answered')) return;
        
        if (!isMulti) {
          options.forEach(opt => opt.classList.remove('selected'));
          option.classList.add('selected');
        } else {
          option.classList.toggle('selected');
        }
      });
    });

    if (submitBtn) {
      submitBtn.addEventListener('click', function() {
        if (block.classList.contains('answered')) return;

        let questionScore = 0;

        if (isMulti) {
          options.forEach(opt => {
            const isCorrectOption = opt.classList.contains('correct');
            const isSelected = opt.classList.contains('selected');
            
            if (isCorrectOption === isSelected) {
              questionScore += 0.25;
            }
          });
        } else {
          const selected = block.querySelector('.option.selected');
          if (selected && selected.classList.contains('correct')) {
            questionScore = 1;
          }
        }

        totalScore += questionScore;
        scoreDisplay.textContent = parseFloat(totalScore.toFixed(2));
        
        block.classList.add('answered');
      });
    }
  });
});
</script>

