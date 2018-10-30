FAQ
===


#### In the architecture doc it states that it will have 'daily data collection'. Is it real-time or up to one day stale?


Figures collects metrics data once a day. The default time is 2:00 am UTC. This can be configured to be a different time of day by adding settings in  `lms.env.json`:

```
{

	...

	"FIGURES": {
			"DAILY_METRICS_IMPORT_HOUR": <integer from 0 to 23>,
			"DAILY_METRICS_IMPORT_MINUTE": <integer from 0 to 59>
		},

	...

}
```
