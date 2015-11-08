# plugins-iot

Scripts that output Nagios format data (0,1,2,3 exit codes and performance data). Can be used in any monitoring system that supports Nagios plugins.

![humidity temperature](https://raw.github.com/dataloop/plugins-iot/master/screenshot.png)

Suggested plugin naming standard is **sensorname.something_human_understandable**. Above example is dht11.temp_humid.py which is being run on a Raspberry Pi2 in the Dataloop office. We'll be adding more scripts over time as we add more sensors and collaborate with others on cool IoT things.

- We'd prefer Python files (but if you have to use something else we'll accept them)
- Script file names should be prefixed with the sensor name
- Put a docstring with instructions at the top of the file

**Pull requests welcome!**
