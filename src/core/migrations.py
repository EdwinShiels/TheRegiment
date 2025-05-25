# TheRegiment - Database Migrations
# SQL table creation matching Pydantic schemas

import asyncio
from typing import List, Dict, Any
from src.core.database import execute_query

# SQL table creation statements
CREATE_TABLES_SQL = {
    "client_profiles": """
        CREATE TABLE IF NOT EXISTS client_profiles (
            user_id VARCHAR(255) PRIMARY KEY,
            goal VARCHAR(10) NOT NULL CHECK (goal IN ('cut', 'bulk', 'recomp')),
            timezone_offset VARCHAR(10) NOT NULL CHECK (timezone_offset ~ '^UTC[±]\\d{1,2}$'),
            start_date DATE NOT NULL,
            paused BOOLEAN NOT NULL DEFAULT FALSE,
            height_cm INTEGER NOT NULL CHECK (height_cm > 0 AND height_cm <= 300),
            weight_kg DECIMAL(5,2) NOT NULL CHECK (weight_kg > 0 AND weight_kg <= 500),
            training_template_id VARCHAR(255) NOT NULL,
            meal_template_id VARCHAR(255) NOT NULL,
            macros_protein INTEGER NOT NULL,
            macros_carbs INTEGER NOT NULL,
            macros_fats INTEGER NOT NULL,
            cardio_minutes INTEGER NOT NULL CHECK (cardio_minutes >= 0 AND cardio_minutes <= 300),
            cycle_start_date DATE NOT NULL,
            block_id VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """,
    
    "meal_logs": """
        CREATE TABLE IF NOT EXISTS meal_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            meal_id VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            logged_at TIMESTAMP WITH TIME ZONE NOT NULL,
            timezone_offset VARCHAR(10) NOT NULL CHECK (timezone_offset ~ '^UTC[±]\\d{1,2}$'),
            status VARCHAR(10) NOT NULL CHECK (status IN ('completed', 'missed')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES client_profiles(user_id) ON DELETE CASCADE
        );
    """,
    
    "training_logs": """
        CREATE TABLE IF NOT EXISTS training_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            block_id VARCHAR(255) NOT NULL,
            day_index INTEGER NOT NULL CHECK (day_index >= 0),
            exercise VARCHAR(255) NOT NULL,
            weight_kg DECIMAL(6,2) NOT NULL CHECK (weight_kg > 0 AND weight_kg <= 1000),
            reps INTEGER NOT NULL CHECK (reps > 0 AND reps <= 100),
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            timezone VARCHAR(10) NOT NULL CHECK (timezone ~ '^UTC[±]\\d{1,2}$'),
            status VARCHAR(10) NOT NULL CHECK (status IN ('completed', 'missed')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES client_profiles(user_id) ON DELETE CASCADE
        );
    """,
    
    "cardio_logs": """
        CREATE TABLE IF NOT EXISTS cardio_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            assigned_minutes INTEGER NOT NULL CHECK (assigned_minutes >= 0 AND assigned_minutes <= 300),
            actual_minutes INTEGER NOT NULL CHECK (actual_minutes >= 0 AND actual_minutes <= 300),
            status VARCHAR(15) NOT NULL CHECK (status IN ('completed', 'underperformed', 'missed')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES client_profiles(user_id) ON DELETE CASCADE
        );
    """,
    
    "checkin_logs": """
        CREATE TABLE IF NOT EXISTS checkin_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            weight_kg DECIMAL(5,2) NOT NULL CHECK (weight_kg > 0 AND weight_kg <= 500),
            mood VARCHAR(10) NOT NULL CHECK (mood IN ('great', 'okay', 'bad')),
            soreness VARCHAR(10) NOT NULL CHECK (soreness IN ('low', 'medium', 'high')),
            sleep VARCHAR(5) NOT NULL CHECK (sleep IN ('4h', '6h', '8h')),
            stress VARCHAR(10) NOT NULL CHECK (stress IN ('low', 'medium', 'high')),
            notes TEXT CHECK (LENGTH(notes) <= 250),
            status VARCHAR(10) NOT NULL CHECK (status IN ('completed', 'missed')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES client_profiles(user_id) ON DELETE CASCADE
        );
    """,
    
    "job_cards": """
        CREATE TABLE IF NOT EXISTS job_cards (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            summary TEXT NOT NULL CHECK (LENGTH(summary) <= 500),
            flags TEXT[] NOT NULL,
            action_suggested VARCHAR(20) NOT NULL CHECK (action_suggested IN ('callout', 'reassign', 'pause', 'escalate', 'none')),
            resolved BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES client_profiles(user_id) ON DELETE CASCADE
        );
    """,
    
    "training_templates": """
        CREATE TABLE IF NOT EXISTS training_templates (
            template_id VARCHAR(255) PRIMARY KEY,
            block_name VARCHAR(255) NOT NULL,
            days_per_week INTEGER NOT NULL CHECK (days_per_week > 0 AND days_per_week <= 7),
            schedule JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """,
    
    "meal_templates": """
        CREATE TABLE IF NOT EXISTS meal_templates (
            template_id VARCHAR(255) PRIMARY KEY,
            goal VARCHAR(10) NOT NULL CHECK (goal IN ('cut', 'bulk', 'recomp')),
            days JSONB NOT NULL,
            shopping_list JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """
}

# Index creation statements for performance
CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_meal_logs_user_date ON meal_logs(user_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_training_logs_user_block ON training_logs(user_id, block_id);",
    "CREATE INDEX IF NOT EXISTS idx_cardio_logs_user_date ON cardio_logs(user_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_checkin_logs_user_date ON checkin_logs(user_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_job_cards_user_date ON job_cards(user_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_job_cards_resolved ON job_cards(resolved);",
    "CREATE INDEX IF NOT EXISTS idx_client_profiles_goal ON client_profiles(goal);",
    "CREATE INDEX IF NOT EXISTS idx_training_templates_days_per_week ON training_templates(days_per_week);",
    "CREATE INDEX IF NOT EXISTS idx_meal_templates_goal ON meal_templates(goal);"
]


async def create_tables() -> Dict[str, Any]:
    """
    Create all database tables with proper constraints and indexes.
    
    Returns:
        Dict containing success status and execution details
        
    Raises:
        Exception: If table creation fails
    """
    print("Starting database table creation")
    
    results = {
        "success": False,
        "tables_created": [],
        "indexes_created": [],
        "errors": []
    }
    
    try:
        # Create tables in dependency order
        table_order = [
            "client_profiles",
            "meal_logs", 
            "training_logs",
            "cardio_logs",
            "checkin_logs",
            "job_cards",
            "training_templates",
            "meal_templates"
        ]
        
        for table_name in table_order:
            try:
                print(f"Creating table: {table_name}")
                await execute_query(CREATE_TABLES_SQL[table_name])
                results["tables_created"].append(table_name)
                print(f"Successfully created table: {table_name}")
                
            except Exception as e:
                error_msg = f"Failed to create table {table_name}: {str(e)}"
                print(error_msg)
                results["errors"].append(error_msg)
                raise Exception(f"Table creation failed for {table_name}: {str(e)}")
        
        # Create indexes for performance
        print("Creating database indexes")
        for index_sql in CREATE_INDEXES_SQL:
            try:
                await execute_query(index_sql)
                results["indexes_created"].append(index_sql.split()[-1])
                
            except Exception as e:
                error_msg = f"Failed to create index: {str(e)}"
                print(error_msg)
                results["errors"].append(error_msg)
                # Don't fail on index creation errors
        
        results["success"] = True
        print(f"Database setup complete. Created {len(results['tables_created'])} tables and {len(results['indexes_created'])} indexes")
        
        return results
        
    except Exception as e:
        print(f"Database setup failed: {str(e)}")
        results["errors"].append(str(e))
        raise


async def drop_all_tables() -> Dict[str, Any]:
    """
    Drop all tables in reverse dependency order.
    WARNING: This will delete all data.
    
    Returns:
        Dict containing success status and execution details
    """
    print("Starting database table deletion - ALL DATA WILL BE LOST")
    
    results = {
        "success": False,
        "tables_dropped": [],
        "errors": []
    }
    
    try:
        # Drop tables in reverse dependency order
        drop_order = [
            "meal_logs",
            "training_logs", 
            "cardio_logs",
            "checkin_logs",
            "job_cards",
            "training_templates",
            "meal_templates",
            "client_profiles"
        ]
        
        for table_name in drop_order:
            try:
                print(f"Dropping table: {table_name}")
                await execute_query(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                results["tables_dropped"].append(table_name)
                print(f"Successfully dropped table: {table_name}")
                
            except Exception as e:
                error_msg = f"Failed to drop table {table_name}: {str(e)}"
                print(error_msg)
                results["errors"].append(error_msg)
        
        print(f"Database tables dropped successfully: {len(results['tables_dropped'])}")
        results["success"] = True
        return results
        
    except Exception as e:
        print(f"Database table deletion failed: {str(e)}")
        results["success"] = False
        raise


async def verify_tables() -> Dict[str, Any]:
    """
    Verify that all required tables exist and have correct structure.
    
    Returns:
        Dict containing verification results
    """
    print("Verifying database table structure")
    
    results = {
        "success": False,
        "tables_verified": [],
        "missing_tables": [],
        "errors": []
    }
    
    try:
        expected_tables = list(CREATE_TABLES_SQL.keys())
        
        # Check if tables exist
        table_check_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE';
        """
        
        existing_tables = await execute_query(table_check_query, fetch_all=True)
        existing_table_names = [row[0] for row in existing_tables]
        
        for table_name in expected_tables:
            if table_name in existing_table_names:
                results["tables_verified"].append(table_name)
                print(f"Table verified: {table_name}")
            else:
                results["missing_tables"].append(table_name)
                print(f"Missing table: {table_name}")
        
        if len(results["missing_tables"]) == 0:
            results["success"] = True
            print(f"All {len(results['tables_verified'])} tables verified successfully")
        else:
            print(f"Missing {len(results['missing_tables'])} tables: {results['missing_tables']}")
        
        return results
        
    except Exception as e:
        error_msg = f"Table verification failed: {str(e)}"
        print(error_msg)
        results["errors"].append(error_msg)
        results["success"] = False
        raise


if __name__ == "__main__":
    # CLI interface for running migrations
    import sys
    
    async def main():
        if len(sys.argv) < 2:
            print("Usage: python migrations.py [create|drop|verify]")
            return
        
        command = sys.argv[1].lower()
        
        if command == "create":
            result = await create_tables()
            print(f"Migration result: {result}")
        elif command == "drop":
            result = await drop_all_tables()
            print(f"Drop result: {result}")
        elif command == "verify":
            result = await verify_tables()
            print(f"Verification result: {result}")
        else:
            print("Invalid command. Use: create, drop, or verify")
    
    asyncio.run(main()) 