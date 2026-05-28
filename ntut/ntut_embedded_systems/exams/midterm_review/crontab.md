> NTUT Embedded Systems <br> Midterm Review <br> Cron Stuff

##
**1. What is the cron daemon?**

> The daemon in a linux system that handles periodic execution. The daemon reads configuration files (crontabs) and executes commands on time.

##
**2. What is the cron command format?**

> minute hour day month weekday command

##
**3. What time and date does this format get translated to?**

```crontab
0 0 14 2 *
```

> On the midnight of Valentine's day

##
**4. What time and date does this format get translated to?**

```crontab
45 10 * * 1-5
```

> 10:45 AM, from Mon to Fri

##
**5. What time and date does this format get translated to?**

```crontab
/3 * * * *
```

> Every three minutes

##
**6. What time and date does this format get translated to?**

```crontab
0,30 * 13 * 5
```

> Every half hour on Friday and every half hour on the 13th