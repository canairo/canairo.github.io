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
  }

  .option:hover {
    border: 1px solid white;
  }

  .quiz-block.answered .option {
    cursor: default;
    pointer-events: none;
  }

  .quiz-block.answered .option.correct {
    background-color: #1c1c1c;
    color: green;
    font-weight: bold;
  }

  .quiz-block.answered .option:not(.correct) {
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
</style>

[recommended listening for this post is do it (yves remix)](https://www.youtube.com/watch?v=kvhVECfGsw8)

apparently wing keong is like an insane crackpot conspiracy theorist? either way the man's a good professor and makes hard tests so if he says that vlan tags cause 9/11 then fuck it man `encapsulation dot1q 9/11` my ass

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
<div class="explanation" markdown="1">
<b>explanation:</b> the only constraint that the router enforces is that no subinterface must overlap (when it receives a packet destined for a specific subnet, it _must_ know which interface to send it to, there cannot be any 'ambiguities'). for each IP address above starting with `192.168.1.x`, the `192.168.1.10/24` will necessarily overlap (because that subnet covers every single `192.168.1.x` addr). `192.168.2.0 255.255.254.0` covers from `192.168.2.0 - 192.168.3.255`, hence no overlap.</div>
</div>
<hr>


<div class="quiz-block" markdown="1">
### question 4

![network topo](https://www.ciscopress.com/content/images/chap4_9780136729358/elementLinks/04fig05_alt.jpg)

consider the network topology, noting that `PC1` and `PC2` are on separate VLANs. `PC1` sends `PC2` an ICMP ping request. assuming that all ARP tables are empty, which of the following is true?

<ul class="quiz-options">
  <li class="option">from S2 to PC2, the packet has a VLAN tag.</li>
  <li class="option">the source MAC address of the packet stays constant throughout the entire lifecycle of the packet.</li>
  <li class="option">when S2 forwards the packet to PC2, it will add PC2's MAC address to its MAC address table.</li>
  <li class="option correct">the packet starts with no VLAN tag, then S1 adds one, then R1 removes and adds another one, then S2 finally removes it.</li>
</ul>

<div class="explanation" markdown=1>
<b>explanation:</b> PCs are 'VLAN unaware', the PC only sends an ethernet packet. VLAN tags are a layer 2 thing, so they are mainly dealt with by switches (as well as layer 3 routers, which need to decapsulate the packet to check its IP, then reapply the next VLAN tag during encapsulation). switches only learn MAC addresses from _source_ MAC addresses and not destinations, and when the router decapsulates the packet, it modifies the source MAC address of the packet to be the router's.
</div>
</div>
<hr>
<!-- QUESTION 5 -->
<div class="quiz-block" markdown="1">
### question 5

same question as above - which of the following is true? (remember the assumption that all ARP, MAC address, and routing tables are empty).

<ul class="quiz-options">
  <li class="option">PC1 will first send an ARP request to PC2 to know which MAC address to send its ICMP packet to.</li>
  <li class="option correct">PC2 will eventually send an ARP response addressed to R1.</li>
  <li class="option">when S1 receives an ARP request, it will flood it out of all 3 ports.</li>
  <li class="option">three ARP requests are sent throughout the process of sending the ICMP request.</li>

</ul>
  <div class="explanation" markdown=1>
<b>explanation:</b>PC1 cannot send an ARP request to PC2 because they are on different subnets! PC1 would send it to the default gateway (the router), and the router would _then send its own ARP request_ to PC2, and PC2 would respond. throughout this process only two ARP requests would be sent (PC1 would need to ARP for its default gateway, and the router would need to ARP for PC2). third option is wrong because a switch floods a broadcast packet out of all ports _except_ ingress, so it would only send 2 packets max (if that).
  </div>
</div>
<hr>

<div class="quiz-block" markdown="1">
### question 6 

i have connected ports g1/1-2 together on DSW1 and S1, and i want to configure etherchannels. which of the following is true? 

<ul class="quiz-options">
  <li class="option">on DSW1's side i configure it as desirable, and on SW1 i configure as auto. i wait until the port channel initiates, then i switch DSW1 to auto. the port channel remains up.</li>
  <li class="option correct">on DSW1's side i configure it as active, and on S1's side i configure it as passive. an etherchannel successfully forms.</li>
  <li class="option">on DSW1's side i configure it as desirable, and on S1's side i configure it as passive. an etherchannel successfully forms.</li>
  <li class="option">on DSW1's side i configure it as desirable, and on S1's side i configure it as on. an etherchannel successfully forms.</li>

</ul>
  <div class="explanation" markdown=1>
<b>explanation:</b> dynamic / auto is for PAGP, active / passive is for LACP, you cannot mix the two. also, an auto/auto won't form, and neither will a passive/passive, but a dynamic/auto and an active / passive will form. for the 'on' option, you need both sides configured as 'on' (this is a mode that does not negotiate any channel).</div>
</div>
<hr>

<script>
document.addEventListener('DOMContentLoaded', function() {
  var options = document.querySelectorAll('.option');
  options.forEach(function(option) {
    option.addEventListener('click', function() {
      var block = event.currentTarget.closest('.quiz-block');
      console.log(block);
      if (block.classList.contains('answered')) return;
      block.classList.add('answered');
    });
  });
});
</script>
