# hallon-saldo
Used to check my kids mobile phone's subscription balances.

Create a config.py in the same directory and fill in:
```
username = 'Your hallon username'
password = 'Your hallon password'
```

Cron job:
```
0 8 * * 5 /path/to/hallon-saldo.py | mail -s "Hallon saldon" -r hallon-saldo@my.domain recipient@my.domain
```
Or if multiple subscriptions for the same user but only interested in one:
```
0 20 * * * /path/to/hallon-saldo.py 0701234567 | mail -s "Hallon saldo" -r hallon-saldo@my.domain recipient@my.domain
```
