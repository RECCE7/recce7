CREATE TABLE IF NOT EXISTS ipInfo (ip TEXT NOT NULL,
                                   plugin_instance TEXT NOT NULL,
                                   timestamp TEXT NOT NULL,
                                   hostname TEXT NULL,
                                   city TEXT NULL,
                                   region TEXT NULL,
                                   country TEXT NULL,
                                   lat REAL CHECK(lat >= -90) CHECK(lat <= 90) NULL,
                                   long REAL CHECK(long >= -180) CHECK(long <= 180) NULL,
                                   org TEXT NULL,
                                   postal TEXT NULL,
                                   PRIMARY KEY(ip,plugin_instance))

