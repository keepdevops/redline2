import os
import duckdb
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def get_enhanced_database_status():
    """Get enhanced database status that includes all database files."""
    try:
        status = {
            'available': True,
            'main_database': '/app/redline_data.duckdb',
            'total_database_files': 0,
            'total_tables': 0,
            'total_records': 0,
            'databases': []
        }
        
        # Check main database
        main_db_tables = 0
        try:
            conn = duckdb.connect('/app/redline_data.duckdb')
            tables = conn.execute('SHOW TABLES').fetchall()
            main_db_tables = len(tables)
            conn.close()
        except Exception as e:
            logger.warning(f"Could not check main database: {e}")
        
        status['main_database_tables'] = main_db_tables
        status['total_tables'] += main_db_tables
        
        # Check converted database files
        converted_dir = '/app/data/converted'
        if os.path.exists(converted_dir):
            db_files = [f for f in os.listdir(converted_dir) if f.endswith('.duckdb')]
            status['total_database_files'] = len(db_files)
            
            # Sample some databases to get table counts
            sample_count = 0
            for db_file in db_files[:10]:  # Check first 10 files for performance
                try:
                    db_path = os.path.join(converted_dir, db_file)
                    conn = duckdb.connect(db_path)
                    tables = conn.execute('SHOW TABLES').fetchall()
                    
                    db_info = {
                        'name': db_file,
                        'tables': len(tables),
                        'size_mb': round(os.path.getsize(db_path) / (1024 * 1024), 2)
                    }
                    
                    # Get record count from first table if exists
                    if tables:
                        try:
                            record_count = conn.execute(f'SELECT COUNT(*) FROM {tables[0][0]}').fetchone()[0]
                            db_info['records'] = record_count
                            status['total_records'] += record_count
                        except:
                            db_info['records'] = 0
                    else:
                        db_info['records'] = 0
                    
                    status['databases'].append(db_info)
                    status['total_tables'] += len(tables)
                    sample_count += 1
                    conn.close()
                    
                except Exception as e:
                    logger.warning(f"Could not check database {db_file}: {e}")
            
            # Estimate total records for remaining databases
            if sample_count > 0 and len(db_files) > sample_count:
                avg_records = status['total_records'] / sample_count if sample_count > 0 else 0
                estimated_additional = avg_records * (len(db_files) - sample_count)
                status['total_records'] += int(estimated_additional)
                status['estimated'] = True
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting enhanced database status: {e}")
        return {
            'available': False,
            'error': str(e)
        }

if __name__ == '__main__':
    import json
    result = get_enhanced_database_status()
    print(json.dumps(result, indent=2))
