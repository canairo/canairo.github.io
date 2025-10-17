---
layout: post
title: project postmortem
date: 2025-10-18 05:40:00 +0800
---

i had to do a uni python proj that involved writing a 'phishing email detector'. it was fun and i liked doing it. here is some overly technical, recherche nonsense about the implementation details of things that i want to talk about.

### project specifications

essentially it just had to be a web app that would take in an email and determine whether or not it was phishing based on some pre-defined criteria. there is not a lot of space for creativity within these criteria (altho i think my teammates did a vv good job of coming up with cool interesting stuff to implement that wasn't specified in the proj requirements) and so a lot of the interesting stuff i encountered was actually in the nitty gritty implementation details of stuff, like:

### big data

so the way our model worked is we would have certain criteria (functions) that wld accept a `ProcessedEmail` class and return an integer. using a labeled dataset of emails (w/ label corresponding to phishing \| non-phishing), collect the `int` avgs of how each category of email 'performs' against the different criteria, which provides a good benchmark w/ which to compare.

```py
class ProcessedEmail:
    def __init__(self, sender: str, 
                       message: str, 
                       subject: str, 
                       attachments: list, 
                       is_phishing: bool,
                       auxiliary_scans_enabled: bool):
        self.sender = sender
        self.message = message
        self.subject = subject
        self.attachments = attachments
        self.is_phishing = is_phishing
        self.auxiliary_scans_enabled = auxiliary_scans_enabled
```

e.g. say for a certain criteria `domain-check` most non-phishing emails score -0.5 around there, and most phishing emails score 0.5. if i test an email and it scores 0.9, it's likely to be phishing, for obvious reasons. we just take our score and see which average it falls towards quicker.
