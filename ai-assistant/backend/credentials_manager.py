"""
Secure Credentials Management System
Handles encrypted storage of database credentials and other sensitive data
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
import getpass
from datetime import datetime

logger = logging.getLogger(__name__)

class CredentialsManager:
    """
    Manages encrypted credentials for various services
    Stores credentials in an encrypted JSON file
    """
    
    def __init__(self, credentials_file: str = None):
        """Initialize the credentials manager"""
        if credentials_file is None:
            # Store in user's home directory for security
            home = Path.home()
            credentials_dir = home / '.ai_assistant' / 'credentials'
            credentials_dir.mkdir(parents=True, exist_ok=True)
            self.credentials_file = credentials_dir / 'credentials.enc'
        else:
            self.credentials_file = Path(credentials_file)
            
        self.key_file = self.credentials_file.parent / 'key.key'
        self.cipher = None
        self._initialize_encryption()
        
    def _initialize_encryption(self):
        """Initialize or load encryption key"""
        if self.key_file.exists():
            # Load existing key
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            # Save key securely
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions on key file (Windows)
            if os.name == 'nt':
                import subprocess
                subprocess.run(['icacls', str(self.key_file), '/inheritance:r'], check=False)
                subprocess.run(['icacls', str(self.key_file), '/grant:r', f'{os.environ.get("USERNAME")}:F'], check=False)
                
        self.cipher = Fernet(key)
        
    def _load_credentials(self) -> Dict[str, Any]:
        """Load and decrypt credentials from file"""
        if not self.credentials_file.exists():
            return {}
            
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return {}
            
    def _save_credentials(self, credentials: Dict[str, Any]):
        """Encrypt and save credentials to file"""
        try:
            json_data = json.dumps(credentials, indent=2)
            encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
                
            # Set restrictive permissions on credentials file (Windows)
            if os.name == 'nt':
                import subprocess
                subprocess.run(['icacls', str(self.credentials_file), '/inheritance:r'], check=False)
                subprocess.run(['icacls', str(self.credentials_file), '/grant:r', f'{os.environ.get("USERNAME")}:F'], check=False)
                
            logger.info("Credentials saved securely")
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            raise
            
    def set_database_credentials(self, 
                                host: str = 'localhost',
                                port: int = 5432,
                                database: str = 'ai_assistant',
                                username: str = 'postgres',
                                password: str = None,
                                save: bool = True) -> Dict[str, Any]:
        """Set database credentials"""
        if password is None:
            # Prompt for password if not provided
            password = getpass.getpass("Enter database password: ")
            
        credentials = self._load_credentials()
        
        if 'databases' not in credentials:
            credentials['databases'] = {}
            
        # Store credentials for this database
        db_key = f"{host}:{port}/{database}"
        credentials['databases'][db_key] = {
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password,
            'last_updated': str(datetime.now())
        }
        
        if save:
            self._save_credentials(credentials)
            
        return credentials['databases'][db_key]
        
    def get_database_credentials(self, 
                                host: str = 'localhost',
                                port: int = 5432,
                                database: str = 'ai_assistant') -> Optional[Dict[str, Any]]:
        """Get database credentials"""
        credentials = self._load_credentials()
        
        if 'databases' not in credentials:
            return None
            
        db_key = f"{host}:{port}/{database}"
        return credentials.get('databases', {}).get(db_key)
        
    def get_database_url(self, 
                        host: str = 'localhost',
                        port: int = 5432,
                        database: str = 'ai_assistant',
                        default_password: str = None) -> str:
        """Get database connection URL"""
        # Try to get stored credentials
        creds = self.get_database_credentials(host, port, database)
        
        if creds:
            username = creds['username']
            password = creds['password']
        else:
            # Use defaults or environment variables
            username = os.environ.get('DB_USER', 'postgres')
            password = os.environ.get('DB_PASSWORD', default_password)
            
            if password is None:
                # For now, use the hardcoded password
                # This should be removed in production
                password = 'root'
                
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
    def set_api_credentials(self, service: str, api_key: str, 
                           additional_data: Dict[str, Any] = None):
        """Set API credentials for a service"""
        credentials = self._load_credentials()
        
        if 'apis' not in credentials:
            credentials['apis'] = {}
            
        credentials['apis'][service] = {
            'api_key': api_key,
            'last_updated': str(datetime.now())
        }
        
        if additional_data:
            credentials['apis'][service].update(additional_data)
            
        self._save_credentials(credentials)
        
    def get_api_credentials(self, service: str) -> Optional[Dict[str, Any]]:
        """Get API credentials for a service"""
        credentials = self._load_credentials()
        return credentials.get('apis', {}).get(service)
        
    def list_stored_services(self) -> Dict[str, List[str]]:
        """List all stored services and databases"""
        credentials = self._load_credentials()
        
        result = {
            'databases': [],
            'apis': []
        }
        
        if 'databases' in credentials:
            result['databases'] = list(credentials['databases'].keys())
            
        if 'apis' in credentials:
            result['apis'] = list(credentials['apis'].keys())
            
        return result
        
    def update_password(self, service_type: str, service_key: str, new_password: str):
        """Update password for a specific service"""
        credentials = self._load_credentials()
        
        if service_type == 'database':
            if 'databases' in credentials and service_key in credentials['databases']:
                credentials['databases'][service_key]['password'] = new_password
                credentials['databases'][service_key]['last_updated'] = str(datetime.now())
                self._save_credentials(credentials)
                return True
        elif service_type == 'api':
            if 'apis' in credentials and service_key in credentials['apis']:
                credentials['apis'][service_key]['api_key'] = new_password
                credentials['apis'][service_key]['last_updated'] = str(datetime.now())
                self._save_credentials(credentials)
                return True
                
        return False
        
    def remove_credentials(self, service_type: str, service_key: str) -> bool:
        """Remove credentials for a specific service"""
        credentials = self._load_credentials()
        
        if service_type == 'database':
            if 'databases' in credentials and service_key in credentials['databases']:
                del credentials['databases'][service_key]
                self._save_credentials(credentials)
                return True
        elif service_type == 'api':
            if 'apis' in credentials and service_key in credentials['apis']:
                del credentials['apis'][service_key]
                self._save_credentials(credentials)
                return True
                
        return False
        
    def export_credentials_template(self, output_file: str = 'credentials_template.json'):
        """Export a template for credentials without sensitive data"""
        credentials = self._load_credentials()
        template = {}
        
        if 'databases' in credentials:
            template['databases'] = {}
            for key, value in credentials['databases'].items():
                template['databases'][key] = {
                    'host': value.get('host'),
                    'port': value.get('port'),
                    'database': value.get('database'),
                    'username': value.get('username'),
                    'password': '<ENTER_PASSWORD_HERE>'
                }
                
        if 'apis' in credentials:
            template['apis'] = {}
            for key in credentials['apis']:
                template['apis'][key] = {
                    'api_key': '<ENTER_API_KEY_HERE>'
                }
                
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=2)
            
        logger.info(f"Credentials template exported to {output_file}")
        return template


# Global instance
credentials_manager = CredentialsManager()

# CLI Interface for managing credentials
if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Manage encrypted credentials')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Set database credentials
    db_parser = subparsers.add_parser('set-db', help='Set database credentials')
    db_parser.add_argument('--host', default='localhost')
    db_parser.add_argument('--port', type=int, default=5432)
    db_parser.add_argument('--database', default='ai_assistant')
    db_parser.add_argument('--username', default='postgres')
    db_parser.add_argument('--password')
    
    # Get database credentials
    get_db_parser = subparsers.add_parser('get-db', help='Get database credentials')
    get_db_parser.add_argument('--host', default='localhost')
    get_db_parser.add_argument('--port', type=int, default=5432)
    get_db_parser.add_argument('--database', default='ai_assistant')
    
    # Set API credentials
    api_parser = subparsers.add_parser('set-api', help='Set API credentials')
    api_parser.add_argument('service', help='Service name (e.g., claude, openai)')
    api_parser.add_argument('--api-key', required=True)
    
    # List stored services
    list_parser = subparsers.add_parser('list', help='List stored services')
    
    # Export template
    export_parser = subparsers.add_parser('export-template', help='Export credentials template')
    export_parser.add_argument('--output', default='credentials_template.json')
    
    args = parser.parse_args()
    
    cm = CredentialsManager()
    
    if args.command == 'set-db':
        creds = cm.set_database_credentials(
            host=args.host,
            port=args.port,
            database=args.database,
            username=args.username,
            password=args.password
        )
        print(f"Database credentials set for {args.host}:{args.port}/{args.database}")
        
    elif args.command == 'get-db':
        creds = cm.get_database_credentials(
            host=args.host,
            port=args.port,
            database=args.database
        )
        if creds:
            print(f"Database: {creds['database']}")
            print(f"Host: {creds['host']}:{creds['port']}")
            print(f"Username: {creds['username']}")
            print(f"Last updated: {creds.get('last_updated', 'Unknown')}")
        else:
            print("No credentials found for this database")
            
    elif args.command == 'set-api':
        cm.set_api_credentials(args.service, args.api_key)
        print(f"API credentials set for {args.service}")
        
    elif args.command == 'list':
        services = cm.list_stored_services()
        print("\nStored Credentials:")
        print("-" * 40)
        if services['databases']:
            print("Databases:")
            for db in services['databases']:
                print(f"  - {db}")
        if services['apis']:
            print("APIs:")
            for api in services['apis']:
                print(f"  - {api}")
                
    elif args.command == 'export-template':
        cm.export_credentials_template(args.output)
        
    else:
        parser.print_help()