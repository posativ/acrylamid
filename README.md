# http://blubee.me

This repo was built with what I consider one of the best SSG out there, it doesn't hur that it's also written in python
[Acrylamid](https://github.com/posativ/acrylamid/) and also [Zurb Foundation 5](http://foundation.zurb.com/)

## Instructions

There's everything required to run this repo on your local system.
Typically while developing I just run

acrylamid autocompile -f && acrylamid view

You'll then be able to view the site on

[localhost](http://localhost:8000)

You can check out the theme/_bb folder to take a look at the foundation 5 stuff. I mainly spent time working on the navigation menu at the top and making sure that my site is responsive to all device sizes.

I decided to go with this setup because it's really fast. Wordpress is bloated and slow and it's only getting more so as time progresses.

In the past I couldn't run a wordpress site with a few plugins on a 2GB dedicated VPS, I am currently running this site on a 512MB shared VPS no problems at all.

You can check out my 99/100 and 100/100 scores for mobile on google pagespeed insights.
[Scores](https://developers.google.com/speed/pagespeed/insights/?url=http%3A%2F%2Fblubee.me)

My site blazes throught most speed tests and that was my main goal, I was tired of wordpress being bloated, easily exploitable system.
