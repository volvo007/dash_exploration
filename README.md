### python Dash exploration

A set of scripts to explore the usage of python Dash.

Right now, the script "uplod.py" is already archived. You can run this script under any python environment (python3 preferred).

It will give an interface like below:

![initial interface](./interface1.jpg "Demo")

You can then upload any Excel or CSV table (must have no empty rows at the beginnig) and you can choose any features you're interested then to check the chart which generated automatically.

The file "exploration.py", which focusing on flash_cache usage, is still under developing.

### Update Log
----------
V0.3 7/18/2019
Add a fuction that allows you to custmize **chart title** and **y-axis title**
Add a fuction that allows you to change the type of chart among 'scatter', 'line chart' or 'scatter + line chart'

V0.2 7/12/2019
Add a function that be able to choose the type of the chart: scatter/line only, or scatter+line

V0.1 7/1/2019:
The first version of the tool.

----------
Necessary libraries (latest version after 7/1/2019):

numpy
pandas
plotly
dash
dash_core_components
dash_core_html
dash_auth
dash_table
flask_caching