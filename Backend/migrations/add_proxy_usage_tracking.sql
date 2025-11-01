-- Add usage tracking columns to proxies table
-- Run this migration to add proxy usage tracking features

-- Add usage_count column (tracks how many times proxy was used)
ALTER TABLE proxies ADD COLUMN usage_count INTEGER DEFAULT 0;

-- Add last_used column (tracks when proxy was last used)
ALTER TABLE proxies ADD COLUMN last_used TIMESTAMP NULL;

-- Update existing proxies to have usage_count = 0
UPDATE proxies SET usage_count = 0 WHERE usage_count IS NULL;

-- Verify migration
SELECT id, host, port, country, is_active, usage_count, last_used FROM proxies LIMIT 5;

