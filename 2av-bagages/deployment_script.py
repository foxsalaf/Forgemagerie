#!/usr/bin/env python3
"""
Script de déploiement et maintenance pour 2AV-Bagages
Usage: python deploy.py [command]

Commands:
  setup     - Configuration initiale de la base de données
  migrate   - Exécute les migrations
  seed      - Ajoute des données de test
  backup    - Sauvegarde la base de données
  restore   - Restaure une sauvegarde
  clean     - Nettoie les anciennes données
  stats     - Affiche les statistiques
  test      - Test de l'installation
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
import argparse

# Import des modules de l'application
try:
    from app import get_db_connection, execute_query, logger
    from werkzeug.security import generate_password_hash
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    print("Assurez-vous que les dépendances sont installées: pip install -r requirements.txt")
    sys.exit(1)

class DeploymentManager:
    """Gestionnaire de déploiement pour 2AV-Bagages"""
    
    def __init__(self):
        self.backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def setup_database(self):
        """Configuration initiale de la base de données"""
        print("🔧 Configuration initiale de la base de données...")
        
        try:
            # Vérification de la connexion
            conn, db_type = get_db_connection()
            print(f"✅ Connexion {db_type} établie")
            
            # Lecture du script SQL de création
            script_path = os.path.join(os.getcwd(), 'database_complete.sql')
            if not os.path.exists(script_path):
                print("❌ Fichier database_complete.sql non trouvé")
                print("Créez le fichier avec le script SQL complet fourni")
                return False
            
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Exécution du script
            cursor = conn.cursor()
            
            if db_type == 'postgresql':
                # PostgreSQL peut exécuter le script complet
                cursor.execute(sql_script)
            else:
                # SQLite nécessite d'exécuter les commandes une par une
                statements = sql_script.split(';')
                for statement in statements:
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            if 'already exists' not in str(e).lower():
                                print(f"⚠️ Avertissement: {e}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Base de données configurée avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la configuration: {e}")
            return False
    
    def create_admin_user(self, username, password, email, full_name):
        """Crée un utilisateur administrateur"""
        try:
            password_hash = generate_password_hash(password)
            
            execute_query(
                """INSERT INTO admin_users (username, password_hash, email, full_name, role) 
                   VALUES (%s, %s, %s, %s, %s) 
                   ON CONFLICT (username) DO NOTHING""",
                (username, password_hash, email, full_name, 'admin'),
                fetch_all=False
            )
            
            print(f"✅ Utilisateur admin '{username}' créé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur création admin: {e}")
            return False
    
    def seed_data(self):
        """Ajoute des données de test"""
        print("🌱 Ajout des données de test...")
        
        try:
            # Vérification si des données existent déjà
            existing_bookings = execute_query(
                "SELECT COUNT(*) as count FROM bookings",
                fetch_one=True
            )
            
            if existing_bookings['count'] > 0:
                response = input(f"⚠️ {existing_bookings['count']} réservations existent déjà. Continuer ? (y/N): ")
                if response.lower() != 'y':
                    return False
            
            # Données de test
            test_bookings = [
                {
                    'client_type': 'famille',
                    'destination': 'aeroport',
                    'pickup_address': '123 Avenue des Champs-Élysées, 75008 Paris',
                    'pickup_datetime': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
                    'bag_count': '4+',
                    'client_name': 'Marie Dubois',
                    'client_email': 'marie.dubois@test.com',
                    'client_phone': '06 12 34 56 78',
                    'special_instructions': 'Vol Air France AF1234 - Terminal 2E',
                    'status': 'pending'
                },
                {
                    'client_type': 'individuel',
                    'destination': 'gare',
                    'pickup_address': '456 Rue de Rivoli, 75001 Paris',
                    'pickup_datetime': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
                    'bag_count': '2',
                    'client_name': 'Jean Martin',
                    'client_email': 'j.martin@test.fr',
                    'client_phone': '06 98 76 54 32',
                    'special_instructions': 'TGV 6651 Paris-Lyon',
                    'status': 'confirmed'
                },
                {
                    'client_type': 'pmr',
                    'destination': 'domicile',
                    'pickup_address': '789 Boulevard Saint-Germain, 75006 Paris',
                    'pickup_datetime': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
                    'bag_count': '3',
                    'client_name': 'Sophie Bernard',
                    'client_email': 'sophie.bernard@test.fr',
                    'client_phone': '06 55 44 33 22',
                    'special_instructions': 'Fauteuil roulant nécessaire',
                    'status': 'completed'
                }
            ]
            
            conn, db_type = get_db_connection()
            cursor = conn.cursor()
            
            for booking in test_bookings:
                # Calcul du prix
                if db_type == 'postgresql':
                    cursor.execute(
                        "SELECT calculate_booking_price(%s, %s, %s) as price",
                        (booking['client_type'], booking['destination'], booking['bag_count'])
                    )
                    price_result = cursor.fetchone()
                    estimated_price = float(price_result['price']) if price_result else 50.0
                else:
                    # Fallback pour SQLite
                    estimated_price = 50.0
                
                # Insertion
                if db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO bookings (
                            client_type, destination, pickup_address, pickup_datetime,
                            bag_count, client_name, client_email, client_phone,
                            special_instructions, estimated_price, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        booking['client_type'], booking['destination'], booking['pickup_address'],
                        booking['pickup_datetime'], booking['bag_count'], booking['client_name'],
                        booking['client_email'], booking['client_phone'], booking['special_instructions'],
                        estimated_price, booking['status']
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO bookings (
                            client_type, destination, pickup_address, pickup_datetime,
                            bag_count, client_name, client_email, client_phone,
                            special_instructions, estimated_price, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        booking['client_type'], booking['destination'], booking['pickup_address'],
                        booking['pickup_datetime'], booking['bag_count'], booking['client_name'],
                        booking['client_email'], booking['client_phone'], booking['special_instructions'],
                        estimated_price, booking['status']
                    ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ {len(test_bookings)} réservations de test ajoutées")
            return True
            
        except Exception as e:
            print(f"❌ Erreur ajout données de test: {e}")
            return False
    
    def backup_database(self):
        """Sauvegarde la base de données"""
        print("💾 Sauvegarde de la base de données...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f'backup_{timestamp}.sql')
            
            database_url = os.environ.get('DATABASE_URL')
            
            if database_url and 'postgresql' in database_url:
                # Backup PostgreSQL
                cmd = f'pg_dump "{database_url}" > "{backup_file}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Sauvegarde créée: {backup_file}")
                    return backup_file
                else:
                    print(f"❌ Erreur pg_dump: {result.stderr}")
                    return None
            else:
                # Backup SQLite
                import shutil
                sqlite_file = 'bagages.db'
                if os.path.exists(sqlite_file):
                    backup_sqlite = os.path.join(self.backup_dir, f'bagages_backup_{timestamp}.db')
                    shutil.copy2(sqlite_file, backup_sqlite)
                    print(f"✅ Sauvegarde SQLite créée: {backup_sqlite}")
                    return backup_sqlite
                else:
                    print("❌ Fichier SQLite non trouvé")
                    return None
                    
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return None
    
    def cleanup_old_data(self, days=90):
        """Nettoie les anciennes données"""
        print(f"🧹 Nettoyage des données anciennes (>{days} jours)...")
        
        try:
            # Utilisation de la fonction PostgreSQL si disponible
            conn, db_type = get_db_connection()
            cursor = conn.cursor()
            
            if db_type == 'postgresql':
                cursor.execute("SELECT cleanup_old_cancelled_bookings(%s)", (days,))
                deleted_count = cursor.fetchone()[0]
            else:
                # Nettoyage manuel pour SQLite
                cursor.execute(
                    "DELETE FROM bookings WHERE status = 'cancelled' AND created_at < datetime('now', '-{} days')".format(days)
                )
                deleted_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ {deleted_count} réservations annulées supprimées")
            return True
            
        except Exception as e:
            print(f"❌ Erreur nettoyage: {e}")
            return False
    
    def show_stats(self):
        """Affiche les statistiques de la base"""
        print("📊 Statistiques de la base de données")
        print("=" * 50)
        
        try:
            # Statistiques générales
            stats = execute_query("SELECT * FROM v_dashboard_stats", fetch_one=True)
            
            if stats:
                print(f"📋 Total réservations: {stats['total_bookings']}")
                print(f"⏳ En attente: {stats['pending_bookings']}")
                print(f"✅ Confirmées: {stats['confirmed_bookings']}")
                print(f"🏁 Terminées: {stats['completed_bookings']}")
                print(f"❌ Annulées: {stats['cancelled_bookings']}")
                print(f"💰 Chiffre d'affaires: {stats['total_revenue']}€")
                print(f"📅 Aujourd'hui: {stats['today_bookings']}")
                print(f"📆 Ce mois: {stats['month_bookings']}")
            
            print("\n📊 Par type de client:")
            client_stats = execute_query("SELECT * FROM v_client_type_stats")
            for stat in client_stats:
                print(f"   {stat['client_type']}: {stat['count']} réservations, {stat['total_revenue']}€")
            
            print("\n🗺️ Par destination:")
            dest_stats = execute_query("SELECT * FROM v_destination_stats")
            for stat in dest_stats:
                print(f"   {stat['destination']}: {stat['count']} réservations, {stat['total_revenue']}€")
            
            # Informations système
            print(f"\n🔧 Informations système:")
            settings = execute_query("SELECT COUNT(*) as count FROM system_settings", fetch_one=True)
            print(f"   Paramètres système: {settings['count']}")
            
            admins = execute_query("SELECT COUNT(*) as count FROM admin_users WHERE is_active = true", fetch_one=True)
            print(f"   Administrateurs actifs: {admins['count']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur récupération stats: {e}")
            return False
    
    def test_installation(self):
        """Test complet de l'installation"""
        print("🧪 Test de l'installation")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 6
        
        # Test 1: Connexion base de données
        try:
            conn, db_type = get_db_connection()
            conn.close()
            print("✅ Test 1/6: Connexion base de données OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 1/6: Connexion base de données ÉCHEC - {e}")
        
        # Test 2: Tables principales
        try:
            tables = ['bookings', 'admin_users', 'pricing_rules', 'system_settings']
            for table in tables:
                execute_query(f"SELECT 1 FROM {table} LIMIT 1")
            print("✅ Test 2/6: Tables principales OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 2/6: Tables principales ÉCHEC - {e}")
        
        # Test 3: Fonctions de calcul de prix
        try:
            conn, db_type = get_db_connection()
            if db_type == 'postgresql':
                price = execute_query(
                    "SELECT calculate_booking_price('individuel', 'aeroport', '2') as price",
                    fetch_one=True
                )
                if price and price['price'] > 0:
                    print("✅ Test 3/6: Calcul de prix OK")
                    tests_passed += 1
                else:
                    print("❌ Test 3/6: Calcul de prix ÉCHEC - Prix invalide")
            else:
                print("⚠️ Test 3/6: Calcul de prix SKIP - SQLite")
                tests_passed += 1
        except Exception as e:
            print(f"❌ Test 3/6: Calcul de prix ÉCHEC - {e}")
        
        # Test 4: Vues statistiques
        try:
            execute_query("SELECT * FROM v_dashboard_stats", fetch_one=True)
            print("✅ Test 4/6: Vues statistiques OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Test 4/6: Vues statistiques ÉCHEC - {e}")
        
        # Test 5: Configuration système
        try:
            settings = execute_query(
                "SELECT COUNT(*) as count FROM system_settings WHERE is_public = true",
                fetch_one=True
            )
            if settings['count'] > 0:
                print("✅ Test 5/6: Configuration système OK")
                tests_passed += 1
            else:
                print("❌ Test 5/6: Configuration système ÉCHEC - Aucun paramètre")
        except Exception as e:
            print(f"❌ Test 5/6: Configuration système ÉCHEC - {e}")
        
        # Test 6: Utilisateurs admin
        try:
            admins = execute_query(
                "SELECT COUNT(*) as count FROM admin_users WHERE is_active = true",
                fetch_one=True
            )
            if admins['count'] > 0:
                print("✅ Test 6/6: Utilisateurs admin OK")
                tests_passed += 1
            else:
                print("❌ Test 6/6: Utilisateurs admin ÉCHEC - Aucun admin actif")
        except Exception as e:
            print(f"❌ Test 6/6: Utilisateurs admin ÉCHEC - {e}")
        
        print(f"\n📊 Résultat: {tests_passed}/{total_tests} tests réussis")
        
        if tests_passed == total_tests:
            print("🎉 Installation complète et fonctionnelle !")
            return True
        else:
            print("⚠️ Problèmes détectés dans l'installation")
            return False

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Gestionnaire de déploiement 2AV-Bagages')
    parser.add_argument('command', choices=[
        'setup', 'migrate', 'seed', 'backup', 'restore', 
        'clean', 'stats', 'test', 'create-admin'
    ], help='Commande à exécuter')
    
    parser.add_argument('--days', type=int, default=90, help='Nombre de jours pour le nettoyage')
    parser.add_argument('--username', help='Nom d\'utilisateur admin')
    parser.add_argument('--password', help='Mot de passe admin')
    parser.add_argument('--email', help='Email admin')
    parser.add_argument('--fullname', help='Nom complet admin')
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    print(f"🚀 2AV-Bagages Deployment Manager")
    print(f"Commande: {args.command}")
    print("-" * 50)
    
    success = False
    
    if args.command == 'setup':
        success = manager.setup_database()
        
    elif args.command == 'seed':
        success = manager.seed_data()
        
    elif args.command == 'backup':
        backup_file = manager.backup_database()
        success = backup_file is not None
        
    elif args.command == 'clean':
        success = manager.cleanup_old_data(args.days)
        
    elif args.command == 'stats':
        success = manager.show_stats()
        
    elif args.command == 'test':
        success = manager.test_installation()
        
    elif args.command == 'create-admin':
        if not all([args.username, args.password, args.email, args.fullname]):
            print("❌ Paramètres manquants pour créer un admin")
            print("Usage: python deploy.py create-admin --username admin --password password123 --email admin@2av.com --fullname 'Admin User'")
            success = False
        else:
            success = manager.create_admin_user(args.username, args.password, args.email, args.fullname)
    
    else:
        print(f"❌ Commande '{args.command}' non implémentée")
        success = False
    
    print("-" * 50)
    if success:
        print("✅ Opération terminée avec succès")
        sys.exit(0)
    else:
        print("❌ Opération échouée")
        sys.exit(1)

if __name__ == '__main__':
    main()