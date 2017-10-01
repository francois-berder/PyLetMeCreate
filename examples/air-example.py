
#!/usr/bin/env python3
"""This example is adapted from the Thermo3 Click wrapper of the LetMeCreate
library.
It reads some values from the sensor and exits.
The Air_quality sensor click was inserted in Mikrobus 1 before running this program.
"""

from letmecreate.core import i2c
from letmecreate.core.common import MIKROBUS_1
# from letmecreate.click import thermo3
from letmecreate.click import air_quality


# Initialise I2C on Mikrobus 1
i2c.init()
i2c.select_bus(MIKROBUS_1)

# Read values
print('{} values from air_quality'.format(air_quality.get_measure(MIKROBUS_1)))

# Release I2C
i2c.release()

