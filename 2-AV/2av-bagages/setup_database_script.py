#!/usr/bin/env python3
"""
Script de configuration de la base de données 2AV-Bagages
Exécute les scripts SQL et initialise les données de test
"""

import os
import sys
from datetime import datetime

def setup_postgresql_database():
    """Configuration pour PostgreSQL (Railway)"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # URL de connexion Railway
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ Variable DATABASE_URL non définie")
            return False
            
        # Correction pour Railway
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        print(f"🔗 Connexion à PostgreSQL...")
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        print("🗄️ Création de la table bookings...")
        
        # Suppression et recréation de la table
        cursor.execute("DROP TABLE IF EXISTS bookings CASCADE;")
        
        cursor.execute("""
            CREATE TABLE bookings (
                id SERIAL PRIMARY KEY,
                client_type VARCHAR(50) NOT NULL CHECK (client_type IN ('individuel', 'famille', 'pmr')),
                destination VARCHAR(50) NOT NULL CHECK (destination IN ('aeroport', 'gare', 'port', 'domicile')),
                pickup_address TEXT NOT NULL,
                pickup_datetime VARCHAR(50) NOT NULL,
                bag_count VARCHAR(10) NOT NULL,
                client_name VARCHAR(100) NOT NULL,
                client_email VARCHAR(100) NOT NULL,
                client_phone VARCHAR(20) NOT NULL,
                special_instructions TEXT,
                estimated_price DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Création des index
        indexes = [
            "CREATE INDEX idx_bookings_status ON bookings(status);",
            "CREATE INDEX idx_bookings_client_type ON bookings(client_type);",
            "CREATE INDEX idx_bookings_destination ON bookings(destination);",
            "CREATE INDEX idx_bookings_created_at ON bookings(created_at);",
            "CREATE INDEX idx_bookings_client_email ON bookings(client_email);"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        print("📊 Insertion des données de test...")
        
        # Données de test
        test_data = [
            # Pending
            ('famille', 'aeroport', '123 Avenue des Champs-Élysées, 75008 Paris', '2024-01-25 14:30', '4+', 'Marie Dubois', 'marie.dubois@gmail.com', '06 12 34 56 78', 'Vol Air France AF1234 - Terminal 2E - Départ 16:30 pour New York', 67.00, 'pending', '2024-01-20 10:30:00'),
            ('individuel', 'gare', '456 Rue de Rivoli, 75001 Paris', '2024-01-25 09:15', '2', 'Jean Martin', 'j.martin@hotmail.fr', '06 98 76 54 32', 'TGV 6651 Paris-Lyon départ 11:45 - Wagon 12 Place 45', 42.00, 'pending', '2024-01-21 15:45:00'),
            ('pmr', 'domicile', '789 Boulevard Saint-Germain, 75006 Paris', '2024-01-25 16:00', '3', 'Sophie Bernard', 'sophie.bernard@yahoo.fr', '06 55 44 33 22', 'Fauteuil roulant nécessaire - Appartement au 3ème étage avec ascenseur', 52.25, 'pending', '2024-01-22 09:20:00'),
            ('famille', 'port', '12 Quai de la Rapée, 75012 Paris', '2024-01-26 08:00', '4+', 'Pierre Moreau', 'p.moreau@free.fr', '07 44 55 66 77', 'Croisière MSC Splendida - Embarquement 10:00 - Cabine 8245', 82.00, 'pending', '2024-01-22 14:15:00'),
            ('individuel', 'aeroport', '34 Avenue Montaigne, 75008 Paris', '2024-01-26 11:20', '1', 'Isabelle Leroy', 'i.leroy@orange.fr', '06 77 88 99 00', 'Vol Lufthansa LH1027 - Terminal 1 - Départ 13:45 pour Munich', 32.00, 'pending', '2024-01-23 08:30:00'),
            
            # Confirmed
            ('famille', 'aeroport', '567 Rue du Faubourg Saint-Honoré, 75008 Paris', '2024-01-24 07:30', '4+', 'Thomas Petit', 'thomas.petit@gmail.com', '06 11 22 33 44', 'Vol Emirates EK073 - Terminal 2C - Départ 09:55 pour Dubaï - Famille avec 2 enfants', 67.00, 'confirmed', '2024-01-18 16:20:00'),
            ('pmr', 'gare', '890 Rue de la Paix, 75002 Paris', '2024-01-24 13:45', '2', 'Monique Rousseau', 'm.rousseau@wanadoo.fr', '06 33 44 55 66', 'TER Lyon-Marseille 17:20 - Assistance nécessaire pour transfert', 39.50, 'confirmed', '2024-01-19 11:45:00'),
            ('individuel', 'domicile', '145 Boulevard Haussmann, 75008 Paris', '2024-01-24 19:00', '3', 'Laurent Dupont', 'l.dupont@sfr.fr', '07 55 66 77 88', 'Retour de voyage d\'affaires - Appartement code 1234A', 55.00, 'confirmed', '2024-01-20 13:25:00'),
            ('famille', 'gare', '78 Avenue de la République, 75011 Paris', '2024-01-27 06:15', '4+', 'Catherine Blanc', 'c.blanc@club-internet.fr', '06 99 00 11 22', 'TGV 5123 Paris-Marseille 08:30 - Vacances familiales - 4 personnes', 63.00, 'confirmed', '2024-01-21 09:10:00'),
            
            # Completed
            ('individuel', 'aeroport', '23 Rue Saint-Antoine, 75004 Paris', '2024-01-20 12:00', '2', 'Nicolas Garnier', 'n.garnier@gmail.com', '06 88 99 00 11', 'Vol British Airways BA0324 - Terminal 2A - Départ 14:30 pour Londres', 42.00, 'completed', '2024-01-15 14:30:00'),
            ('famille', 'port', '456 Quai de Jemmapes, 75010 Paris', '2024-01-19 15:30', '4+', 'Sylvie Moreau', 's.moreau@hotmail.com', '07 22 33 44 55', 'Croisière Costa Pacifica - Embarquement 17:30 - Méditerranée 7 jours', 82.00, 'completed', '2024-01-14 10:15:00'),
            ('pmr', 'domicile', '789 Avenue Parmentier, 75011 Paris', '2024-01-18 14:15', '1', 'André Fabre', 'a.fabre@orange.fr', '06 44 55 66 77', 'Retour d\'hospitalisation - Matériel médical dans bagage', 20.75, 'completed', '2024-01-16 08:45:00'),
            ('individuel', 'gare', '101 Rue de Charonne, 75011 Paris', '2024-01-17 10:30', '3', 'Julie Mercier', 'j.mercier@free.fr', '06 66 77 88 99', 'TGV 9247 Paris-Toulouse 12:45 - Déménagement partiel', 55.00, 'completed', '2024-01-12 16:20:00'),
            ('famille', 'aeroport', '234 Rue des Martyrs, 75018 Paris', '2024-01-16 05:45', '4+', 'Patrick Roux', 'p.roux@wanadoo.fr', '07 00 11 22 33', 'Vol long-courrier Air France AF0083 - Terminal 2E - Départ 08:20 pour Tokyo', 67.00, 'completed', '2024-01-10 12:30:00'),
            ('individuel', 'domicile', '67 Boulevard Voltaire, 75011 Paris', '2024-01-15 20:00', '2', 'Valérie Simon', 'v.simon@sfr.fr', '06 55 77 99 11', 'Retour de week-end - Pas d\'ascenseur, 2ème étage', 37.00, 'completed', '2024-01-13 11:40:00'),
            
            # Cancelled
            ('individuel', 'aeroport', '145 Rue de la Roquette, 75011 Paris', '2024-01-22 16:30', '1', 'Michel Durand', 'm.durand@gmail.com', '06 77 88 99 22', 'Vol annulé par la compagnie - Remboursement demandé', 32.00, 'cancelled', '2024-01-18 09:15:00'),
            ('famille', 'gare', '89 Avenue de la Nation, 75012 Paris', '2024-01-23 11:00', '4+', 'Christiane Leduc', 'c.leduc@club-internet.fr', '07 33 44 55 88', 'Changement de programme - Voyage reporté', 63.00, 'cancelled', '2024-01-19 15:30:00')
        ]
        
        # Insertion des données
        cursor.executemany("""
            INSERT INTO bookings (
                client_type, destination, pickup_address, pickup_datetime, 
                bag_count, client_name, client_email, client_phone, 
                special_instructions, estimated_price, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, test_data)
        
        # Création du trigger pour updated_at
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $ LANGUAGE plpgsql;
        """)
        
        cursor.execute("""
            CREATE TRIGGER update_bookings_updated_at
                BEFORE UPDATE ON bookings
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        
        # Vérification
        cursor.execute("SELECT COUNT(*) FROM bookings")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(estimated_price), 0) FROM bookings WHERE status = 'completed'")
        revenue = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ PostgreSQL configuré avec succès !")
        print(f"📊 {count} réservations créées")
        print(f"⏳ {pending} en attente")
        print(f"💰 {revenue}€ de chiffre d'affaires")
        
        return True
        
    except ImportError:
        print("❌ psycopg2 non installé. Installez-le avec: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False

def setup_sqlite_database():
    """Configuration pour SQLite (développement local)"""
    try:
        import sqlite3
        
        print("🔗 Connexion à SQLite...")
        conn = sqlite3.connect('bagages.db')
        cursor = conn.cursor()
        
        print("🗄️ Création de la table bookings...")
        
        # Suppression et recréation de la table
        cursor.execute("DROP TABLE IF EXISTS bookings")
        
        cursor.execute("""
            CREATE TABLE bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_type TEXT NOT NULL CHECK (client_type IN ('individuel', 'famille', 'pmr')),
                destination TEXT NOT NULL CHECK (destination IN ('aeroport', 'gare', 'port', 'domicile')),
                pickup_address TEXT NOT NULL,
                pickup_datetime TEXT NOT NULL,
                bag_count TEXT NOT NULL,
                client_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                client_phone TEXT NOT NULL,
                special_instructions TEXT,
                estimated_price REAL NOT NULL,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Création des index
        indexes = [
            "CREATE INDEX idx_bookings_status ON bookings(status)",
            "CREATE INDEX idx_bookings_client_type ON bookings(client_type)",
            "CREATE INDEX idx_bookings_destination ON bookings(destination)",
            "CREATE INDEX idx_bookings_created_at ON bookings(created_at)",
            "CREATE INDEX idx_bookings_client_email ON bookings(client_email)"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        print("📊 Insertion des données de test...")
        
        # Mêmes données de test mais pour SQLite
        test_data = [
            # Pending
            ('famille', 'aeroport', '123 Avenue des Champs-Élysées, 75008 Paris', '2024-01-25 14:30', '4+', 'Marie Dubois', 'marie.dubois@gmail.com', '06 12 34 56 78', 'Vol Air France AF1234 - Terminal 2E - Départ 16:30 pour New York', 67.00, 'pending', '2024-01-20 10:30:00'),
            ('individuel', 'gare', '456 Rue de Rivoli, 75001 Paris', '2024-01-25 09:15', '2', 'Jean Martin', 'j.martin@hotmail.fr', '06 98 76 54 32', 'TGV 6651 Paris-Lyon départ 11:45 - Wagon 12 Place 45', 42.00, 'pending', '2024-01-21 15:45:00'),
            ('pmr', 'domicile', '789 Boulevard Saint-Germain, 75006 Paris', '2024-01-25 16:00', '3', 'Sophie Bernard', 'sophie.bernard@yahoo.fr', '06 55 44 33 22', 'Fauteuil roulant nécessaire - Appartement au 3ème étage avec ascenseur', 52.25, 'pending', '2024-01-22 09:20:00'),
            ('famille', 'port', '12 Quai de la Rapée, 75012 Paris', '2024-01-26 08:00', '4+', 'Pierre Moreau', 'p.moreau@free.fr', '07 44 55 66 77', 'Croisière MSC Splendida - Embarquement 10:00 - Cabine 8245', 82.00, 'pending', '2024-01-22 14:15:00'),
            ('individuel', 'aeroport', '34 Avenue Montaigne, 75008 Paris', '2024-01-26 11:20', '1', 'Isabelle Leroy', 'i.leroy@orange.fr', '06 77 88 99 00', 'Vol Lufthansa LH1027 - Terminal 1 - Départ 13:45 pour Munich', 32.00, 'pending', '2024-01-23 08:30:00'),
            
            # Confirmed
            ('famille', 'aeroport', '567 Rue du Faubourg Saint-Honoré, 75008 Paris', '2024-01-24 07:30', '4+', 'Thomas Petit', 'thomas.petit@gmail.com', '06 11 22 33 44', 'Vol Emirates EK073 - Terminal 2C - Départ 09:55 pour Dubaï - Famille avec 2 enfants', 67.00, 'confirmed', '2024-01-18 16:20:00'),
            ('pmr', 'gare', '890 Rue de la Paix, 75002 Paris', '2024-01-24 13:45', '2', 'Monique Rousseau', 'm.rousseau@wanadoo.fr', '06 33 44 55 66', 'TER Lyon-Marseille 17:20 - Assistance nécessaire pour transfert', 39.50, 'confirmed', '2024-01-19 11:45:00'),
            ('individuel', 'domicile', '145 Boulevard Haussmann, 75008 Paris', '2024-01-24 19:00', '3', 'Laurent Dupont', 'l.dupont@sfr.fr', '07 55 66 77 88', 'Retour de voyage d\'affaires - Appartement code 1234A', 55.00, 'confirmed', '2024-01-20 13:25:00'),
            ('famille', 'gare', '78 Avenue de la République, 75011 Paris', '2024-01-27 06:15', '4+', 'Catherine Blanc', 'c.blanc@club-internet.fr', '06 99 00 11 22', 'TGV 5123 Paris-Marseille 08:30 - Vacances familiales - 4 personnes', 63.00, 'confirmed', '2024-01-21 09:10:00'),
            
            # Completed
            ('individuel', 'aeroport', '23 Rue Saint-Antoine, 75004 Paris', '2024-01-20 12:00', '2', 'Nicolas Garnier', 'n.garnier@gmail.com', '06 88 99 00 11', 'Vol British Airways BA0324 - Terminal 2A - Départ 14:30 pour Londres', 42.00, 'completed', '2024-01-15 14:30:00'),
            ('famille', 'port', '456 Quai de Jemmapes, 75010 Paris', '2024-01-19 15:30', '4+', 'Sylvie Moreau', 's.moreau@hotmail.com', '07 22 33 44 55', 'Croisière Costa Pacifica - Embarquement 17:30 - Méditerranée 7 jours', 82.00, 'completed', '2024-01-14 10:15:00'),
            ('pmr', 'domicile', '789 Avenue Parmentier, 75011 Paris', '2024-01-18 14:15', '1', 'André Fabre', 'a.fabre@orange.fr', '06 44 55 66 77', 'Retour d\'hospitalisation - Matériel médical dans bagage', 20.75, 'completed', '2024-01-16 08:45:00'),
            ('individuel', 'gare', '101 Rue de Charonne, 75011 Paris', '2024-01-17 10:30', '3', 'Julie Mercier', 'j.mercier@free.fr', '06 66 77 88 99', 'TGV 9247 Paris-Toulouse 12:45 - Déménagement partiel', 55.00, 'completed', '2024-01-12 16:20:00'),
            ('famille', 'aeroport', '234 Rue des Martyrs, 75018 Paris', '2024-01-16 05:45', '4+', 'Patrick Roux', 'p.roux@wanadoo.fr', '07 00 11 22 33', 'Vol long-courrier Air France AF0083 - Terminal 2E - Départ 08:20 pour Tokyo', 67.00, 'completed', '2024-01-10 12:30:00'),
            ('individuel', 'domicile', '67 Boulevard Voltaire, 75011 Paris', '2024-01-15 20:00', '2', 'Valérie Simon', 'v.simon@sfr.fr', '06 55 77 99 11', 'Retour de week-end - Pas d\'ascenseur, 2ème étage', 37.00, 'completed', '2024-01-13 11:40:00'),
            
            # Cancelled
            ('individuel', 'aeroport', '145 Rue de la Roquette, 75011 Paris', '2024-01-22 16:30', '1', 'Michel Durand', 'm.durand@gmail.com', '06 77 88 99 22', 'Vol annulé par la compagnie - Remboursement demandé', 32.00, 'cancelled', '2024-01-18 09:15:00'),
            ('famille', 'gare', '89 Avenue de la Nation, 75012 Paris', '2024-01-23 11:00', '4+', 'Christiane Leduc', 'c.leduc@club-internet.fr', '07 33 44 55 88', 'Changement de programme - Voyage reporté', 63.00, 'cancelled', '2024-01-19 15:30:00')
        ]
        
        # Insertion des données
        cursor.executemany("""
            INSERT INTO bookings (
                client_type, destination, pickup_address, pickup_datetime, 
                bag_count, client_name, client_email, client_phone, 
                special_instructions, estimated_price, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_data)
        
        conn.commit()
        
        # Vérification
        cursor.execute("SELECT COUNT(*) FROM bookings")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(estimated_price), 0) FROM bookings WHERE status = 'completed'")
        revenue = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ SQLite configuré avec succès !")
        print(f"📊 {count} réservations créées")
        print(f"⏳ {pending} en attente")
        print(f"💰 {revenue}€ de chiffre d'affaires")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur SQLite: {e}")
        return False

def display_stats():
    """Affiche les statistiques de la base de données"""
    try:
        # Essai PostgreSQL d'abord
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            db_type = "PostgreSQL"
        else:
            import sqlite3
            conn = sqlite3.connect('bagages.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            db_type = "SQLite"
        
        print(f"\n📊 STATISTIQUES BASE DE DONNÉES ({db_type})")
        print("=" * 50)
        
        # Statistiques générales
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled
            FROM bookings
        """)
        
        stats = cursor.fetchone()
        print(f"📋 Total réservations: {stats[0] if db_type == 'SQLite' else stats['total']}")
        print(f"⏳ En attente: {stats[1] if db_type == 'SQLite' else stats['pending']}")
        print(f"✅ Confirmées: {stats[2] if db_type == 'SQLite' else stats['confirmed']}")
        print(f"🎯 Terminées: {stats[3] if db_type == 'SQLite' else stats['completed']}")
        print(f"❌ Annulées: {stats[4] if db_type == 'SQLite' else stats['cancelled']}")
        
        # Chiffre d'affaires
        cursor.execute("SELECT COALESCE(SUM(estimated_price), 0) FROM bookings WHERE status = 'completed'")
        revenue = cursor.fetchone()[0]
        print(f"💰 Chiffre d'affaires: {revenue:.2f}€")
        
        # Par type de client
        print("\n👥 RÉPARTITION PAR TYPE DE CLIENT")
        cursor.execute("""
            SELECT client_type, COUNT(*) as count, AVG(estimated_price) as avg_price
            FROM bookings 
            GROUP BY client_type 
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            if db_type == 'SQLite':
                print(f"   {row[0]}: {row[1]} réservations (prix moyen: {row[2]:.2f}€)")
            else:
                print(f"   {row['client_type']}: {row['count']} réservations (prix moyen: {row['avg_price']:.2f}€)")
        
        # Par destination
        print("\n🎯 RÉPARTITION PAR DESTINATION")
        cursor.execute("""
            SELECT destination, COUNT(*) as count, AVG(estimated_price) as avg_price
            FROM bookings 
            GROUP BY destination 
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            if db_type == 'SQLite':
                print(f"   {row[0]}: {row[1]} réservations (prix moyen: {row[2]:.2f}€)")
            else:
                print(f"   {row['destination']}: {row['count']} réservations (prix moyen: {row['avg_price']:.2f}€)")
        
        # Dernières réservations
        print(f"\n📅 DERNIÈRES RÉSERVATIONS")
        cursor.execute("""
            SELECT client_name, destination, estimated_price, status, created_at
            FROM bookings 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            if db_type == 'SQLite':
                print(f"   {row[0]} - {row[1]} - {row[2]:.2f}€ - {row[3]} - {row[4]}")
            else:
                print(f"   {row['client_name']} - {row['destination']} - {row['estimated_price']:.2f}€ - {row['status']} - {row['created_at']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des statistiques: {e}")

def main():
    """Fonction principale"""
    print("🚀 CONFIGURATION BASE DE DONNÉES 2AV-BAGAGES")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        print("🔍 DATABASE_URL détectée - Configuration PostgreSQL")
        success = setup_postgresql_database()
    else:
        print("🔍 Aucune DATABASE_URL - Configuration SQLite locale")
        success = setup_sqlite_database()
    
    if success:
        print("\n🎉 Configuration terminée avec succès !")
        display_stats()
        print(f"\n✅ Vous pouvez maintenant lancer votre application Flask:")
        print(f"   python app.py")
        print(f"\n🔐 Interface admin accessible à:")
        print(f"   http://localhost:5000/admin/login")
        print(f"   Identifiants: admin / admin123")
    else:
        print("\n❌ Échec de la configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()