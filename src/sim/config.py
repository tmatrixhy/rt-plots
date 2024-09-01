import os

# postgres database
DB_NAME = os.getenv("POSTGRES_DB", "rt-plots")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# database client
DB_BUFFERS = os.getenv("DB_BUFFERS", 5)
DB_BUFFER_LEN = os.getenv("DB_BUFFER_LEN", 500)

# sims
NUM_SIMS = os.getenv("NUM_SIMS", 4)
SIM_FREQ_LOW = os.getenv("SIM_FREQ_LOW", 20)
SIM_FREQ_HIGH = os.getenv("SIM_FREQ_HIGH", 50)
