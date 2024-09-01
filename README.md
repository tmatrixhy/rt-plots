# rt-simulator - No more public updates will be made to this repo

Monte Carlo simulator with:
* uniform sampling defined by previous value + (current default = [-5,5])
* random sampling rate Hz per simulator - (current default = [20,50])  
* ~~real-time data feed and plotting to a browser front-end~~ removed per suggestion from @luisvillamil
* postgres backend
* grafana for data visualization

# pre-requisites:  

* Linux based OS
* [python 3.12^](https://www.python.org/downloads/)
* [poetry](https://python-poetry.org/)
* [docker](https://docs.docker.com/engine/install/)

# install & run

```
make service-setup && make service-clear # will require sudo
make service-up
poetry install
poetry run python -m src.sim
```

Due to some quirks of Grafana you will have to manually configure the Dashboard.

1. Open your browser and navigate to Grafana, default url should be: `http://127.0.0.1:3000` 
2. Visit the `Connections -> Data sources` page and select the `rt-plots` data source. 
3. Click the password box (you do not have to edit values), scroll down and hit "Save & test" a few times until you get a confirmation.
4. A default dashboard is provided for you in `./scripts/default_dashboard.json`. Copy the contents and go to Dashboards -> New -> Import. Paste the JSON and select `rt-plots` as the Data Source.
5. Data should start populating now.

# service configuration

Postgres and Grafana services are setup with the `make service-up` command in the base directory, all configuration is performed through environment variables set in `./scripts/sample.env`. The postgres data source is added using the grafana REST API via  `./scripts/setup-grafana.sh`.

* modify `./scripts/sample.env` to set env vars for services
* view / understand the `./Makefile`  

# application mods

In `src/sim/simulator.py` 
* Alter `MonteCarloSimulation.run_simulation` to modify stepping.
* Alter `MonteCarloSimulation.sample` to modify sampling method.

In `src/sim/statistics.py`
* Add any function that begins with `proc_` to have it called each time a step is made in `MonteCarloSimulation.run_simulation`
* To send statistics back to the simulator, at the end of your `proc_` function, declare a class variable prepended with `_s_` and set the value to anything you'd like. eg: `self._s_sum = sum(self.sample_queue)` and `{"sum":32}` will be returned as part of the processing step in the calling function.
