-- ==========================================================
-- 1. SUPPRESSION DES TABLES (pour repartir à zéro)
-- ==========================================================
DROP TABLE IF EXISTS commandes;
DROP TABLE IF EXISTS produits;
DROP TABLE IF EXISTS clients;

-- ==========================================================
-- 2. CRÉATION DES TABLES
-- ==========================================================

-- Table des Clients
CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    ville VARCHAR(100),
    date_inscription DATE DEFAULT CURRENT_DATE
);

-- Table des Produits
CREATE TABLE produits (
    produit_id SERIAL PRIMARY KEY,
    nom_produit VARCHAR(100) NOT NULL,
    categorie VARCHAR(50),
    prix_unitaire DECIMAL(10, 2) NOT NULL
);

-- Table des Commandes
CREATE TABLE commandes (
    commande_id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(client_id) ON DELETE CASCADE,
    produit_id INT REFERENCES produits(produit_id) ON DELETE CASCADE,
    quantite INT CHECK (quantite > 0),
    date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================================
-- 3. IMPLÉMENTATION DES DONNÉES (Génération aléatoire)
-- ==========================================================

-- A. Insertion de 5 produits fixes (pour servir de base)
INSERT INTO produits (nom_produit, categorie, prix_unitaire) VALUES
('Ordinateur Portable', 'Électronique', 899.99),
('Souris Sans Fil', 'Accessoires', 25.50),
('Clavier Mécanique', 'Accessoires', 75.00),
('Écran 27 pouces', 'Électronique', 199.00),
('Casque Audio', 'Accessoires', 55.00);

-- B. Insertion de 1000 clients aléatoires
INSERT INTO clients (nom, email, ville)
SELECT 
    'Client_' || i, 
    'user' || i || '@email.com',
    (ARRAY['Paris', 'Lyon', 'Lille', 'Bordeaux', 'Marseille', 'Nantes', 'Strasbourg'])[floor(random() * 7 + 1)]
FROM generate_series(1, 1000) s(i);

-- C. Insertion de 5000 commandes aléatoires
-- On pioche des clients entre 1 et 1000 et des produits entre 1 et 5
INSERT INTO commandes (client_id, produit_id, quantite, date_commande)
SELECT 
    floor(random() * 1000 + 1)::int, 
    floor(random() * 5 + 1)::int,    
    floor(random() * 10 + 1)::int, 
    NOW() - (random() * (interval '365 days'))
FROM generate_series(1, 5000) s(i);

-- ==========================================================
-- 4. REQUETES
-- ==========================================================
-- A.Nous al


