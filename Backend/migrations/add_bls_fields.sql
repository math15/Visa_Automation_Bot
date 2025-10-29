-- Migration: Add BLS-specific fields to match BLS registration form exactly
-- Run this migration to update existing database schema

-- Add new columns to accounts table
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS sur_name VARCHAR(100);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS passport_type_guid VARCHAR(255);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS passport_issue_country_guid VARCHAR(255);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS birth_country_guid VARCHAR(255);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS country_of_residence_guid VARCHAR(255);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS country_code VARCHAR(10) DEFAULT '+213';

-- Update existing data
UPDATE accounts SET sur_name = family_name WHERE sur_name IS NULL;
UPDATE accounts SET country_code = phone_country_code WHERE country_code IS NULL;

-- Modify existing columns to match BLS requirements
ALTER TABLE accounts ALTER COLUMN passport_issue_place SET NOT NULL;
ALTER TABLE accounts ALTER COLUMN passport_type TYPE VARCHAR(255);
ALTER TABLE accounts ALTER COLUMN birth_country TYPE VARCHAR(255);
ALTER TABLE accounts ALTER COLUMN country_of_residence TYPE VARCHAR(255);

COMMENT ON COLUMN accounts.sur_name IS 'BLS: SurName (Family Name) - optional';
COMMENT ON COLUMN accounts.first_name IS 'BLS: FirstName (Given Name) - required';
COMMENT ON COLUMN accounts.last_name IS 'BLS: LastName - required';
COMMENT ON COLUMN accounts.passport_issue_place IS 'BLS: IssuePlace - REQUIRED field!';
COMMENT ON COLUMN accounts.passport_type_guid IS 'BLS: PassportType GUID from dropdown';
COMMENT ON COLUMN accounts.passport_issue_country_guid IS 'BLS: BirthCountry GUID from dropdown';
COMMENT ON COLUMN accounts.birth_country_guid IS 'BLS: BirthCountry GUID from dropdown';
COMMENT ON COLUMN accounts.country_of_residence_guid IS 'BLS: CountryOfResidence GUID from dropdown';
COMMENT ON COLUMN accounts.country_code IS 'BLS: CountryCode field (+213 for Algeria)';

