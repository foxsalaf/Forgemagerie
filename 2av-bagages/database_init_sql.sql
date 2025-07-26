-- =====================================================
-- SCRIPTS SQL COMPLETS POUR 2AV-BAGAGES
-- =====================================================

-- =====================================================
-- 1. CRÉATION DE LA TABLE BOOKINGS (PostgreSQL)
-- =====================================================

-- Pour PostgreSQL (Railway)
DROP TABLE IF EXISTS bookings CASCADE;

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

-- Index pour améliorer les performances
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_client_type ON bookings(client_type);
CREATE INDEX idx_bookings_destination ON bookings(destination);
CREATE INDEX idx_bookings_created_at ON bookings(created_at);
CREATE INDEX idx_bookings_client_email ON bookings(client_email);

-- =====================================================
-- 2. CRÉATION DE LA TABLE BOOKINGS (SQLite)
-- =====================================================

-- Pour SQLite (développement local)
/*
DROP TABLE IF EXISTS bookings;

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
);

CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_client_type ON bookings(client_type);
CREATE INDEX idx_bookings_destination ON bookings(destination);
CREATE INDEX idx_bookings_created_at ON bookings(created_at);
*/

-- =====================================================
-- 3. INSERTION DES DONNÉES DE TEST RÉALISTES
-- =====================================================

-- Réservations PENDING (En attente)
INSERT INTO bookings (
    client_type, destination, pickup_address, pickup_datetime, 
    bag_count, client_name, client_email, client_phone, 
    special_instructions, estimated_price, status, 
    created_at, updated_at
) VALUES 
-- Réservations en attente
(
    'famille', 'aeroport', 
    '123 Avenue des Champs-Élysées, 75008 Paris', 
    '2024-01-25 14:30', 
    '4+', 'Marie Dubois', 'marie.dubois@gmail.com', '06 12 34 56 78',
    'Vol Air France AF1234 - Terminal 2E - Départ 16:30 pour New York', 
    67.00, 'pending',
    '2024-01-20 10:30:00', '2024-01-20 10:30:00'
),
(
    'individuel', 'gare', 
    '456 Rue de Rivoli, 75001 Paris', 
    '2024-01-25 09:15', 
    '2', 'Jean Martin', 'j.martin@hotmail.fr', '06 98 76 54 32',
    'TGV 6651 Paris-Lyon départ 11:45 - Wagon 12 Place 45', 
    42.00, 'pending',
    '2024-01-21 15:45:00', '2024-01-21 15:45:00'
),
(
    'pmr', 'domicile', 
    '789 Boulevard Saint-Germain, 75006 Paris', 
    '2024-01-25 16:00', 
    '3', 'Sophie Bernard', 'sophie.bernard@yahoo.fr', '06 55 44 33 22',
    'Fauteuil roulant nécessaire - Appartement au 3ème étage avec ascenseur', 
    52.25, 'pending',
    '2024-01-22 09:20:00', '2024-01-22 09:20:00'
),
(
    'famille', 'port', 
    '12 Quai de la Rapée, 75012 Paris', 
    '2024-01-26 08:00', 
    '4+', 'Pierre Moreau', 'p.moreau@free.fr', '07 44 55 66 77',
    'Croisière MSC Splendida - Embarquement 10:00 - Cabine 8245', 
    82.00, 'pending',
    '2024-01-22 14:15:00', '2024-01-22 14:15:00'
),
(
    'individuel', 'aeroport', 
    '34 Avenue Montaigne, 75008 Paris', 
    '2024-01-26 11:20', 
    '1', 'Isabelle Leroy', 'i.leroy@orange.fr', '06 77 88 99 00',
    'Vol Lufthansa LH1027 - Terminal 1 - Départ 13:45 pour Munich', 
    32.00, 'pending',
    '2024-01-23 08:30:00', '2024-01-23 08:30:00'
);

-- Réservations CONFIRMED (Confirmées)
INSERT INTO bookings (
    client_type, destination, pickup_address, pickup_datetime, 
    bag_count, client_name, client_email, client_phone, 
    special_instructions, estimated_price, status, 
    created_at, updated_at
) VALUES 
(
    'famille', 'aeroport', 
    '567 Rue du Faubourg Saint-Honoré, 75008 Paris', 
    '2024-01-24 07:30', 
    '4+', 'Thomas Petit', 'thomas.petit@gmail.com', '06 11 22 33 44',
    'Vol Emirates EK073 - Terminal 2C - Départ 09:55 pour Dubaï - Famille avec 2 enfants', 
    67.00, 'confirmed',
    '2024-01-18 16:20:00', '2024-01-23 10:15:00'
),
(
    'pmr', 'gare', 
    '890 Rue de la Paix, 75002 Paris', 
    '2024-01-24 13:45', 
    '2', 'Monique Rousseau', 'm.rousseau@wanadoo.fr', '06 33 44 55 66',
    'TER Lyon-Marseille 17:20 - Assistance nécessaire pour transfert', 
    39.50, 'confirmed',
    '2024-01-19 11:45:00', '2024-01-23 14:30:00'
),
(
    'individuel', 'domicile', 
    '145 Boulevard Haussmann, 75008 Paris', 
    '2024-01-24 19:00', 
    '3', 'Laurent Dupont', 'l.dupont@sfr.fr', '07 55 66 77 88',
    'Retour de voyage d\'affaires - Appartement code 1234A', 
    55.00, 'confirmed',
    '2024-01-20 13:25:00', '2024-01-23 16:45:00'
),
(
    'famille', 'gare', 
    '78 Avenue de la République, 75011 Paris', 
    '2024-01-27 06:15', 
    '4+', 'Catherine Blanc', 'c.blanc@club-internet.fr', '06 99 00 11 22',
    'TGV 5123 Paris-Marseille 08:30 - Vacances familiales - 4 personnes', 
    63.00, 'confirmed',
    '2024-01-21 09:10:00', '2024-01-24 08:20:00'
);

-- Réservations COMPLETED (Terminées)
INSERT INTO bookings (
    client_type, destination, pickup_address, pickup_datetime, 
    bag_count, client_name, client_email, client_phone, 
    special_instructions, estimated_price, status, 
    created_at, updated_at
) VALUES 
(
    'individuel', 'aeroport', 
    '23 Rue Saint-Antoine, 75004 Paris', 
    '2024-01-20 12:00', 
    '2', 'Nicolas Garnier', 'n.garnier@gmail.com', '06 88 99 00 11',
    'Vol British Airways BA0324 - Terminal 2A - Départ 14:30 pour Londres', 
    42.00, 'completed',
    '2024-01-15 14:30:00', '2024-01-20 15:45:00'
),
(
    'famille', 'port', 
    '456 Quai de Jemmapes, 75010 Paris', 
    '2024-01-19 15:30', 
    '4+', 'Sylvie Moreau', 's.moreau@hotmail.com', '07 22 33 44 55',
    'Croisière Costa Pacifica - Embarquement 17:30 - Méditerranée 7 jours', 
    82.00, 'completed',
    '2024-01-14 10:15:00', '2024-01-19 18:00:00'
),
(
    'pmr', 'domicile', 
    '789 Avenue Parmentier, 75011 Paris', 
    '2024-01-18 14:15', 
    '1', 'André Fabre', 'a.fabre@orange.fr', '06 44 55 66 77',
    'Retour d\'hospitalisation - Matériel médical dans bagage', 
    20.75, 'completed',
    '2024-01-16 08:45:00', '2024-01-18 16:30:00'
),
(
    'individuel', 'gare', 
    '101 Rue de Charonne, 75011 Paris', 
    '2024-01-17 10:30', 
    '3', 'Julie Mercier', 'j.mercier@free.fr', '06 66 77 88 99',
    'TGV 9247 Paris-Toulouse 12:45 - Déménagement partiel', 
    55.00, 'completed',
    '2024-01-12 16:20:00', '2024-01-17 13:15:00'
),
(
    'famille', 'aeroport', 
    '234 Rue des Martyrs, 75018 Paris', 
    '2024-01-16 05:45', 
    '4+', 'Patrick Roux', 'p.roux@wanadoo.fr', '07 00 11 22 33',
    'Vol long-courrier Air France AF0083 - Terminal 2E - Départ 08:20 pour Tokyo', 
    67.00, 'completed',
    '2024-01-10 12:30:00', '2024-01-16 09:30:00'
),
(
    'individuel', 'domicile', 
    '67 Boulevard Voltaire, 75011 Paris', 
    '2024-01-15 20:00', 
    '2', 'Valérie Simon', 'v.simon@sfr.fr', '06 55 77 99 11',
    'Retour de week-end - Pas d\'ascenseur, 2ème étage', 
    37.00, 'completed',
    '2024-01-13 11:40:00', '2024-01-15 21:15:00'
);

-- Réservations CANCELLED (Annulées)
INSERT INTO bookings (
    client_type, destination, pickup_address, pickup_datetime, 
    bag_count, client_name, client_email, client_phone, 
    special_instructions, estimated_price, status, 
    created_at, updated_at
) VALUES 
(
    'individuel', 'aeroport', 
    '145 Rue de la Roquette, 75011 Paris', 
    '2024-01-22 16:30', 
    '1', 'Michel Durand', 'm.durand@gmail.com', '06 77 88 99 22',
    'Vol annulé par la compagnie - Remboursement demandé', 
    32.00, 'cancelled',
    '2024-01-18 09:15:00', '2024-01-21 14:20:00'
),
(
    'famille', 'gare', 
    '89 Avenue de la Nation, 75012 Paris', 
    '2024-01-23 11:00', 
    '4+', 'Christiane Leduc', 'c.leduc@club-internet.fr', '07 33 44 55 88',
    'Changement de programme - Voyage reporté', 
    63.00, 'cancelled',
    '2024-01-19 15:30:00', '2024-01-22 10:45:00'
);

-- =====================================================
-- 4. VUES UTILES POUR LES STATISTIQUES
-- =====================================================

-- Vue pour les statistiques par statut
CREATE OR REPLACE VIEW bookings_stats AS
SELECT 
    status,
    COUNT(*) as count,
    SUM(estimated_price) as total_revenue,
    AVG(estimated_price) as avg_price,
    MIN(created_at) as oldest_booking,
    MAX(created_at) as newest_booking
FROM bookings 
GROUP BY status;

-- Vue pour les statistiques par type de client
CREATE OR REPLACE VIEW client_type_stats AS
SELECT 
    client_type,
    COUNT(*) as count,
    SUM(estimated_price) as total_revenue,
    AVG(estimated_price) as avg_price
FROM bookings 
GROUP BY client_type;

-- Vue pour les statistiques par destination
CREATE OR REPLACE VIEW destination_stats AS
SELECT 
    destination,
    COUNT(*) as count,
    SUM(estimated_price) as total_revenue,
    AVG(estimated_price) as avg_price
FROM bookings 
GROUP BY destination;

-- Vue pour les réservations récentes (7 derniers jours)
CREATE OR REPLACE VIEW recent_bookings AS
SELECT *
FROM bookings
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC;

-- =====================================================
-- 5. FONCTIONS UTILES
-- =====================================================

-- Fonction pour calculer le prix selon les tarifs 2AV-Bagages
CREATE OR REPLACE FUNCTION calculate_booking_price(
    p_client_type VARCHAR(50),
    p_destination VARCHAR(50),
    p_bag_count VARCHAR(10)
) RETURNS DECIMAL(10,2) AS $$
DECLARE
    base_price DECIMAL(10,2);
    destination_supplement DECIMAL(10,2);
    num_bags INTEGER;
    total_price DECIMAL(10,2);
BEGIN
    -- Prix de base par bagage selon le type de client
    CASE p_client_type
        WHEN 'pmr' THEN base_price := 15.75;
        WHEN 'famille' THEN base_price := 13.75;
        WHEN 'individuel' THEN base_price := 17.00;
        ELSE base_price := 17.00;
    END CASE;
    
    -- Supplément selon la destination
    CASE p_destination
        WHEN 'aeroport' THEN destination_supplement := 15.00;
        WHEN 'gare' THEN destination_supplement := 8.00;
        WHEN 'port' THEN destination_supplement := 12.00;
        WHEN 'domicile' THEN destination_supplement := 5.00;
        ELSE destination_supplement := 10.00;
    END CASE;
    
    -- Nombre de bagages
    CASE p_bag_count
        WHEN '1' THEN num_bags := 1;
        WHEN '2' THEN num_bags := 2;
        WHEN '3' THEN num_bags := 3;
        WHEN '4+' THEN num_bags := 4;
        ELSE num_bags := 1;
    END CASE;
    
    -- Calcul total
    total_price := (base_price * num_bags) + destination_supplement;
    
    RETURN total_price;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. TRIGGERS POUR MISE À JOUR AUTOMATIQUE
-- =====================================================

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 7. REQUÊTES DE VÉRIFICATION
-- =====================================================

-- Vérifier les données insérées
SELECT 'Total bookings' as metric, COUNT(*) as value FROM bookings
UNION ALL
SELECT 'Pending bookings', COUNT(*) FROM bookings WHERE status = 'pending'
UNION ALL
SELECT 'Confirmed bookings', COUNT(*) FROM bookings WHERE status = 'confirmed'
UNION ALL
SELECT 'Completed bookings', COUNT(*) FROM bookings WHERE status = 'completed'
UNION ALL
SELECT 'Cancelled bookings', COUNT(*) FROM bookings WHERE status = 'cancelled'
UNION ALL
SELECT 'Total revenue', SUM(estimated_price)::INTEGER FROM bookings WHERE status = 'completed';

-- Afficher un échantillon des données
SELECT 
    id,
    client_name,
    client_type,
    destination,
    estimated_price,
    status,
    created_at::date as created_date
FROM bookings 
ORDER BY created_at DESC 
LIMIT 10;

-- =====================================================
-- 8. REQUÊTES POUR L'INTERFACE ADMIN
-- =====================================================

-- Statistiques pour le dashboard
SELECT 
    (SELECT COUNT(*) FROM bookings) as total_bookings,
    (SELECT COUNT(*) FROM bookings WHERE status = 'pending') as pending_bookings,
    (SELECT COALESCE(SUM(estimated_price), 0) FROM bookings WHERE status = 'completed') as total_revenue,
    (SELECT COUNT(*) FROM bookings WHERE DATE(created_at) = CURRENT_DATE) as today_bookings;

-- Réservations récentes pour le dashboard
SELECT * FROM bookings 
ORDER BY created_at DESC 
LIMIT 10;

-- Recherche par client
SELECT * FROM bookings 
WHERE 
    LOWER(client_name) LIKE LOWER('%martin%') 
    OR LOWER(client_email) LIKE LOWER('%martin%')
    OR client_phone LIKE '%martin%'
ORDER BY created_at DESC;

-- =====================================================
-- 9. PROCÉDURES DE MAINTENANCE
-- =====================================================

-- Procédure pour nettoyer les anciennes réservations annulées
CREATE OR REPLACE FUNCTION cleanup_old_cancelled_bookings(days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM bookings 
    WHERE status = 'cancelled' 
    AND created_at < CURRENT_DATE - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Procédure pour archiver les anciennes réservations terminées
CREATE OR REPLACE FUNCTION archive_old_completed_bookings(days_old INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Ici vous pourriez créer une table d'archive et y déplacer les données
    -- Pour l'exemple, on compte juste
    SELECT COUNT(*) INTO archived_count
    FROM bookings 
    WHERE status = 'completed' 
    AND created_at < CURRENT_DATE - INTERVAL '1 day' * days_old;
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 10. COMMENTAIRES ET DOCUMENTATION
-- =====================================================

COMMENT ON TABLE bookings IS 'Table principale des réservations 2AV-Bagages';
COMMENT ON COLUMN bookings.client_type IS 'Type de client: individuel, famille, pmr';
COMMENT ON COLUMN bookings.destination IS 'Destination: aeroport, gare, port, domicile';
COMMENT ON COLUMN bookings.pickup_address IS 'Adresse de collecte des bagages';
COMMENT ON COLUMN bookings.pickup_datetime IS 'Date et heure de collecte';
COMMENT ON COLUMN bookings.bag_count IS 'Nombre de bagages: 1, 2, 3, 4+';
COMMENT ON COLUMN bookings.estimated_price IS 'Prix estimé en euros';
COMMENT ON COLUMN bookings.status IS 'Statut: pending, confirmed, completed, cancelled';
COMMENT ON COLUMN bookings.special_instructions IS 'Instructions spéciales du client';

-- =====================================================
-- FIN DU SCRIPT - BASE DE DONNÉES PRÊTE !
-- =====================================================