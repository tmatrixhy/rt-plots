# rt-plots

Monte Carlo simulator with:
* uniform sampling defined by previous value + [-5,5]
* random sampling rate [5,10] Hz per simulator  
* real-time data feed and plotting to a browser front-end

# pre-requisites:  

* [python 3.12^](https://www.python.org/downloads/)
* [poetry](https://python-poetry.org/)

# install & run

```
poetry install
poetry run python -m src.sim
```

Open browser and navigate to `http://127.0.0.1:5000`
