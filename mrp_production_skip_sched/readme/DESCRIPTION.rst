Prevents thas sheduler is triggered when a production is confirmed or changed
once confirmed.
Scheduler cron or manual execution should do the trick instead.

This could be achieved setting ``stock.no_auto_scheduler`` config parameter,
but it should affect to other processes, like pickings.

