# plugins-iot

Scripts that output Nagios format data (0,1,2,3 exit codes and performance data). Can be used in any monitoring system that supports Nagios plugins.

![humidity temperature](https://raw.github.com/dataloop/plugins-iot/master/screenshot.png)

Suggested plugin naming standard is **sensorname.something_human_understandable**. Above example is dht11.temp_humid.py which is being run on a Raspberry Pi2 in the Dataloop office. We'll be adding more scripts over time as we add more sensors and collaborate with others on cool IoT things.

We'd prefer all plugins to be written in Python as we bundle an interpreter for that with our agent. But we'll accept plugins in any langauge in this repo.

**Pull requests welcome!**
