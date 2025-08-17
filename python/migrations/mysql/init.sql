-- MySQL Initialization Script
-- Set proper character encoding and create functions

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Enable event scheduler for maintenance tasks
SET GLOBAL event_scheduler = ON;

-- Create UUID function if not exists (for older MySQL versions)
DELIMITER $$
CREATE FUNCTION IF NOT EXISTS UUID_V4() RETURNS CHAR(36)
DETERMINISTIC
BEGIN
    RETURN LOWER(CONCAT(
        HEX(RANDOM_BYTES(4)),
        '-', HEX(RANDOM_BYTES(2)),
        '-', HEX(RANDOM_BYTES(2)),
        '-', HEX(RANDOM_BYTES(2)),
        '-', HEX(RANDOM_BYTES(6))
    ));
END$$
DELIMITER ;