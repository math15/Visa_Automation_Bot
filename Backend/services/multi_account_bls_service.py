"""
BLS Account Creation Service for Multi-Account Management
Handles concurrent BLS account creation for multiple accounts
"""

import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from sqlalchemy.orm import Session
from datetime import datetime

from models.database import Account
from services.bls_modules import BLSAccountCreator
from main import BLSAccountCreate


class MultiAccountBLSService:
    """Service for managing BLS account creation for multiple accounts"""
    
    def __init__(self):
        self.bls_creator = BLSAccountCreator()
        self.max_concurrent = 5  # Maximum concurrent BLS creations
        
    async def create_bls_accounts_concurrent(
        self, 
        account_ids: List[int], 
        db: Session
    ) -> Dict[str, Any]:
        """Create BLS accounts for multiple accounts concurrently"""
        try:
            logger.info(f"Starting concurrent BLS creation for {len(account_ids)} accounts")
            
            # Get accounts to process
            accounts = db.query(Account).filter(
                Account.id.in_(account_ids),
                Account.bls_status == "creating"
            ).all()
            
            if not accounts:
                return {
                    "success": False,
                    "message": "No accounts found for BLS creation",
                    "results": []
                }
            
            # Create semaphore to limit concurrent operations
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            # Create tasks for concurrent processing
            tasks = []
            for account in accounts:
                task = self._create_single_bls_account(account, db, semaphore)
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful = 0
            failed = 0
            detailed_results = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Account {accounts[i].id} failed with exception: {result}")
                    failed += 1
                    detailed_results.append({
                        "account_id": accounts[i].id,
                        "email": accounts[i].email,
                        "success": False,
                        "error": str(result)
                    })
                elif result.get("success"):
                    successful += 1
                    detailed_results.append({
                        "account_id": accounts[i].id,
                        "email": accounts[i].email,
                        "success": True,
                        "bls_username": result.get("bls_username"),
                        "message": result.get("message")
                    })
                else:
                    failed += 1
                    detailed_results.append({
                        "account_id": accounts[i].id,
                        "email": accounts[i].email,
                        "success": False,
                        "error": result.get("error", "Unknown error")
                    })
            
            logger.info(f"BLS creation completed: {successful} successful, {failed} failed")
            
            return {
                "success": True,
                "message": f"BLS creation completed: {successful} successful, {failed} failed",
                "successful_count": successful,
                "failed_count": failed,
                "results": detailed_results
            }
            
        except Exception as e:
            logger.error(f"Error in concurrent BLS creation: {e}")
            return {
                "success": False,
                "message": f"Error in concurrent BLS creation: {str(e)}",
                "results": []
            }
    
    async def _create_single_bls_account(
        self, 
        account: Account, 
        db: Session, 
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Create BLS account for a single account"""
        async with semaphore:
            try:
                logger.info(f"Creating BLS account for: {account.email}")
                
                # Convert Account to BLSAccountCreate
                account_data = BLSAccountCreate(
                    first_name=account.first_name,
                    last_name=account.last_name,
                    family_name=account.family_name,
                    date_of_birth=datetime.strptime(account.date_of_birth, "%Y-%m-%d"),
                    gender=account.gender,
                    marital_status=account.marital_status,
                    passport_number=account.passport_number,
                    passport_type=account.passport_type,
                    passport_issue_date=datetime.strptime(account.passport_issue_date, "%Y-%m-%d"),
                    passport_expiry_date=datetime.strptime(account.passport_expiry_date, "%Y-%m-%d"),
                    passport_issue_place=account.passport_issue_place,
                    passport_issue_country=account.passport_issue_country,
                    email=account.email,
                    mobile=account.mobile,
                    phone_country_code=account.phone_country_code,
                    birth_country=account.birth_country,
                    country_of_residence=account.country_of_residence,
                    number_of_members=account.number_of_members,
                    relationship=account.relationship,
                    primary_applicant=account.primary_applicant,
                    password=account.password
                )
                
                # Create BLS account using browser flow (RECOMMENDED - bypasses WAF)
                # Use create_account_with_browser instead of create_account for better success rate
                result = await self.bls_creator.create_account_with_browser(account_data, db)
                
                # Update account status based on result
                if result.success:
                    account.bls_status = "created"
                    account.status = "bls_created"
                    account.bls_username = result.account_id
                    account.bls_created_at = datetime.utcnow()
                    account.bls_error_message = None
                    logger.info(f"BLS account created successfully for: {account.email}")
                else:
                    account.bls_status = "failed"
                    account.status = "bls_failed"
                    account.bls_error_message = result.error_message
                    logger.error(f"BLS account creation failed for: {account.email} - {result.error_message}")
                
                # Update processing info
                account.last_processing_attempt = datetime.utcnow()
                account.last_activity = datetime.utcnow()
                
                # Commit changes
                db.commit()
                
                return {
                    "success": result.success,
                    "message": result.message,
                    "bls_username": result.account_id,
                    "error": result.error_message
                }
                
            except Exception as e:
                logger.error(f"Error creating BLS account for {account.email}: {e}")
                
                # Update account status to failed
                account.bls_status = "failed"
                account.status = "bls_failed"
                account.bls_error_message = str(e)
                account.last_processing_attempt = datetime.utcnow()
                
                db.commit()
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def retry_failed_accounts(
        self, 
        account_ids: Optional[List[int]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Retry BLS creation for failed accounts"""
        try:
            logger.info("Retrying failed BLS account creations")
            
            # Get failed accounts
            query = db.query(Account).filter(Account.bls_status == "failed")
            if account_ids:
                query = query.filter(Account.id.in_(account_ids))
            
            failed_accounts = query.all()
            
            if not failed_accounts:
                return {
                    "success": True,
                    "message": "No failed accounts found to retry",
                    "results": []
                }
            
            # Reset status to creating
            for account in failed_accounts:
                account.bls_status = "creating"
                account.status = "bls_creating"
                account.bls_error_message = None
            
            db.commit()
            
            # Start concurrent creation
            account_ids_list = [account.id for account in failed_accounts]
            result = await self.create_bls_accounts_concurrent(account_ids_list, db)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrying failed accounts: {e}")
            return {
                "success": False,
                "message": f"Error retrying failed accounts: {str(e)}",
                "results": []
            }
    
    async def get_processing_status(
        self, 
        account_ids: List[int],
        db: Session
    ) -> Dict[str, Any]:
        """Get processing status for multiple accounts"""
        try:
            accounts = db.query(Account).filter(Account.id.in_(account_ids)).all()
            
            status_summary = {
                "total": len(accounts),
                "not_created": 0,
                "creating": 0,
                "created": 0,
                "failed": 0
            }
            
            detailed_status = []
            
            for account in accounts:
                status_summary[account.bls_status] += 1
                detailed_status.append({
                    "account_id": account.id,
                    "email": account.email,
                    "bls_status": account.bls_status,
                    "status": account.status,
                    "processing_attempts": account.processing_attempts,
                    "last_processing_attempt": account.last_processing_attempt,
                    "bls_error_message": account.bls_error_message
                })
            
            return {
                "success": True,
                "status_summary": status_summary,
                "detailed_status": detailed_status
            }
            
        except Exception as e:
            logger.error(f"Error getting processing status: {e}")
            return {
                "success": False,
                "message": f"Error getting processing status: {str(e)}"
            }


# Global instance
multi_account_bls_service = MultiAccountBLSService()
