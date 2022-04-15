# Argumentation-based Negotiation 

## Introduction

This project implements the modernisation of a negotiation protocol based on the proposed argumentation framework.
Agents 

Our agents are able to:
- Communicate between each other
- Propose an engine
- Accept or refuse an engine
- Enter in a negotiation
- Counter-argue on an engine choice

### Setup

You must clone this repository

    git clone https://github.com/alexfrst/ArgumentationBasedNegotiation.git

Then install requirements

    pip install -r requirements.txt

### Runnable scripts

You can run a negotiation with the following command:

    python pwArgumentAgent.py

You can run negotiation in batch with stats computing with the folowing command:

    python pwArgumentAgentBatch.py    

# Technical details

## Architecture

    TODO tree to be inserted

## Implementation details
The most interesting part of this project is the implementation of the negotiation protocol in the `pwAgentArgument` file.
We have added some attributes:
- counter_arguments: that stores the counter-arguments already given for a given item.
- arguments: that stores the pro-arguments already given for a given item.  

The step function dispatches treatment of the incoming message depending on the type of the message (PROPOSE, ASK_WHY, COMMIT, ...).

To avoid loops in the negotiation process, we have added some rules: 
- An item can be proposed only once
- While negotiating for an item, an agent can talk about criterion once.

## Agents

We have four agents, Alice, Bob, Eve and John. We made them argue two by two and we have assessed their performance.


