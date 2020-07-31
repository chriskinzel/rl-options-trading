--
-- File generated with SQLiteStudio v3.2.1 on Tue Jul 28 15:41:03 2020
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: historical_data
DROP TABLE IF EXISTS historical_data;

CREATE TABLE historical_data (
    underlying      TEXT (32)      NOT NULL
                                   COLLATE BINARY,
    underlying_last DECIMAL (6, 3) NOT NULL,
    optionroot      TEXT (64)      NOT NULL
                                   COLLATE BINARY,
    type            CHAR (1)       NOT NULL,
    expiration      INTEGER        NOT NULL,
    quotedate       INTEGER        NOT NULL,
    strike          DECIMAL (6, 3) NOT NULL,
    last            DECIMAL (6, 3) NOT NULL,
    bid             DECIMAL (6, 3) NOT NULL,
    ask             DECIMAL (6, 3) NOT NULL,
    impliedvol      DECIMAL (3, 6) NOT NULL,
    delta           DECIMAL (3, 6) NOT NULL,
    gamma           DECIMAL (3, 6) NOT NULL,
    theta           DECIMAL (3, 6) NOT NULL,
    vega            DECIMAL (3, 6) NOT NULL,
    PRIMARY KEY (
        optionroot,
        quotedate ASC
    )
)
WITHOUT ROWID;


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
