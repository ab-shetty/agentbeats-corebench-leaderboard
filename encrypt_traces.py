#!/usr/bin/env python3
"""Collect trace files, combine into JSONL, and encrypt with password."""

import argparse
import json
import tarfile
import io
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def collect_traces(traces_dir: Path) -> list:
    """Collect all run_summary_*.json files and sort by task number."""
    trace_files = []
    
    # Find all run_summary_*.json files
    for trace_file in traces_dir.rglob("run_summary_*.json"):
        # Extract run_id from filename: run_summary_{run_id}.json
        filename = trace_file.name
        if filename.startswith("run_summary_") and filename.endswith(".json"):
            run_id = filename[len("run_summary_"):-len(".json")]
            
            with open(trace_file, 'r') as f:
                data = json.load(f)
                
            # Extract task number from the data (assuming it's in the JSON)
            # Adjust this based on your actual trace structure
            task_num = data.get('task_index', data.get('task_number', 999999))
            
            trace_files.append({
                'task_num': task_num,
                'run_id': run_id,
                'data': data,
                'path': trace_file
            })
    
    # Sort by task number
    trace_files.sort(key=lambda x: x['task_num'])
    
    return trace_files


def create_combined_jsonl(trace_files: list) -> str:
    """Create JSONL content from sorted trace files."""
    lines = []
    for trace in trace_files:
        lines.append(json.dumps(trace['data']))
    return '\n'.join(lines)


def encrypt_content(content: str, password: str) -> bytes:
    """Encrypt content using password-based encryption."""
    # Use a fixed salt for reproducibility (so the same password always works)
    # In production, you might want a random salt stored with the file
    salt = b'agentbeats_trace_encryption_salt_v1'
    
    key = derive_key(password, salt)
    fernet = Fernet(key)
    
    encrypted = fernet.encrypt(content.encode('utf-8'))
    return encrypted


def create_encrypted_archive(jsonl_content: str, password: str, output_path: Path):
    """Create encrypted tar.gz archive containing the JSONL."""
    # Encrypt the JSONL content
    encrypted_data = encrypt_content(jsonl_content, password)
    
    # Create tar.gz with encrypted data
    with tarfile.open(output_path, 'w:gz') as tar:
        # Create in-memory file
        encrypted_file = io.BytesIO(encrypted_data)
        tarinfo = tarfile.TarInfo(name='traces.encrypted.jsonl')
        tarinfo.size = len(encrypted_data)
        tar.addfile(tarinfo, encrypted_file)
    
    # Also save metadata file with decryption instructions
    metadata = {
        'encryption': 'Fernet (AES-128)',
        'password': 'reproducibility',
        'format': 'JSONL (one trace per line)',
        'decryption_example': '''
# To decrypt:
import tarfile
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

password = "reproducibility"
salt = b'agentbeats_trace_encryption_salt_v1'

kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
fernet = Fernet(key)

with tarfile.open('traces.encrypted.tar.gz', 'r:gz') as tar:
    encrypted_file = tar.extractfile('traces.encrypted.jsonl')
    encrypted_data = encrypted_file.read()
    decrypted = fernet.decrypt(encrypted_data)
    traces_jsonl = decrypted.decode('utf-8')
    print(traces_jsonl)
'''
    }
    
    metadata_path = output_path.parent / 'DECRYPTION_INSTRUCTIONS.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Collect, combine, and encrypt trace files')
    parser.add_argument('--traces-dir', type=Path, required=True, help='Directory containing trace subdirectories')
    parser.add_argument('--output', type=Path, required=True, help='Output path for encrypted archive')
    parser.add_argument('--password', type=str, default='reproducibility', help='Encryption password')
    
    args = parser.parse_args()
    
    if not args.traces_dir.exists():
        print(f"Error: Traces directory {args.traces_dir} does not exist")
        return 1
    
    # Collect and sort traces
    print(f"Collecting traces from {args.traces_dir}...")
    trace_files = collect_traces(args.traces_dir)
    
    if not trace_files:
        print("Warning: No trace files found")
        return 0
    
    print(f"Found {len(trace_files)} trace files")
    
    # Create combined JSONL
    print("Creating combined JSONL...")
    jsonl_content = create_combined_jsonl(trace_files)
    
    # Encrypt and create archive
    print(f"Encrypting with password '{args.password}'...")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    create_encrypted_archive(jsonl_content, args.password, args.output)
    
    print(f"✓ Created encrypted archive: {args.output}")
    print(f"✓ Size: {args.output.stat().st_size / (1024*1024):.2f} MB")
    print(f"✓ Decryption instructions: {args.output.parent / 'DECRYPTION_INSTRUCTIONS.json'}")
    
    return 0


if __name__ == '__main__':
    exit(main())